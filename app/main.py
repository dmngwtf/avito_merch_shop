import os
import jwt
import bcrypt
from fastapi import FastAPI, Depends, HTTPException, status, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv

from app.database import Base, engine, SessionLocal
from app.models import User, CoinTransaction, InventoryItem
from app.schemas import (
    AuthRequest,
    AuthResponse,
    SendCoinRequest,
    InfoResponse,
    ErrorResponse,
    CoinHistoryItem,
    CoinHistory,
    InventoryItem as InventorySchema
)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "TEST_SECRET_KEY")
MERC_ITEMS = {
    "t-shirt": 80,
    "cup": 20,
    "book": 50,
    "pen": 10,
    "powerbank": 200,
    "hoody": 300,
    "umbrella": 200,
    "socks": 10,
    "wallet": 50,
    "pink-hoody": 500
}

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Avito shop",
    version="1.0.0"
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token.")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")


@app.post("/api/auth", response_model=AuthResponse, responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def auth_user(body: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user:
        # Create a new user for simplicity or raise an error if needed
        hashed_pw = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
        new_user = User(username=body.username, hashed_password=hashed_pw)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user
    else:
        # Verify password
        if not bcrypt.checkpw(body.password.encode(), user.hashed_password.encode()):
            raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm="HS256")
    return AuthResponse(token=token)


@app.get("/api/info", response_model=InfoResponse, responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def get_info(current_user: User = Depends(authenticate_token), db: Session = Depends(get_db)):
    # Build Inventory
    inventory_db = db.query(InventoryItem).filter(InventoryItem.user_id == current_user.id).all()
    inventory = []
    for item in inventory_db:
        inventory.append(InventorySchema(type=item.item_type, quantity=item.quantity))

    # Build Coin History
    received_transactions = []
    for t in current_user.received_transactions:
        if t.from_user:
            received_transactions.append(CoinHistoryItem(fromUser=t.from_user.username, amount=t.amount))
    
    sent_transactions = []
    for t in current_user.sent_transactions:
        if t.to_user:
            sent_transactions.append(CoinHistoryItem(toUser=t.to_user.username, amount=t.amount))

    coin_history = {
        "received": received_transactions,
        "sent": sent_transactions
    }

    return InfoResponse(
        coins=current_user.coins,
        inventory=inventory,
        coinHistory=coin_history
    )


@app.post("/api/sendCoin", responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def send_coin(body: SendCoinRequest, current_user: User = Depends(authenticate_token), db: Session = Depends(get_db)):
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive.")
    if current_user.coins < body.amount:
        raise HTTPException(status_code=400, detail="Insufficient coins.")

    recipient = db.query(User).filter(User.username == body.toUser).first()
    if not recipient:
        raise HTTPException(status_code=400, detail="Recipient not found.")

    current_user.coins -= body.amount
    recipient.coins += body.amount

    transaction = CoinTransaction(from_user_id=current_user.id, to_user_id=recipient.id, amount=body.amount)
    db.add(transaction)
    db.commit()

    return {"message": "Coins sent successfully"}


@app.get("/api/buy/{item}", responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def buy_item(
    item: str = Path(..., description="Item name to purchase"),
    current_user: User = Depends(authenticate_token),
    db: Session = Depends(get_db)
):
    if item not in MERC_ITEMS:
        raise HTTPException(status_code=400, detail="Unsupported item.")

    cost = MERC_ITEMS[item]
    if current_user.coins < cost:
        raise HTTPException(status_code=400, detail="Not enough coins to buy this item.")

    # Deduct coins
    current_user.coins -= cost

    # Add to inventory
    inv_item = (
        db.query(InventoryItem).filter(InventoryItem.user_id == current_user.id, InventoryItem.item_type == item).first()
    )
    if inv_item:
        inv_item.quantity += 1
    else:
        inv_item = InventoryItem(user_id=current_user.id, item_type=item, quantity=1)
        db.add(inv_item)

    db.commit()
    return {"message": f"{item} purchased successfully."}