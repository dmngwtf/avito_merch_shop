import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    """Use the in-memory test DB instead of the real one."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.mark.integration
def test_auth_and_buy_item():
    """
    1. Authenticate or register user.
    2. Check initial coin balance.
    3. Buy an item, verify coin decrement.
    """
    resp = client.post("/api/auth", json={"username": "test_user", "password": "secret"})
    assert resp.status_code == 200
    token = resp.json()["token"]

    # Check info
    info_resp = client.get("/api/info", headers={"Authorization": f"Bearer {token}"})
    assert info_resp.status_code == 200
    initial_coins = info_resp.json()["coins"]
    assert initial_coins == 1000

    # Buy an item (cup = 20)
    buy_resp = client.get("/api/buy/cup", headers={"Authorization": f"Bearer {token}"})
    assert buy_resp.status_code == 200
    assert buy_resp.json()["message"] == "cup purchased successfully."

    # Check coin balance after purchase
    info_after_buy = client.get("/api/info", headers={"Authorization": f"Bearer {token}"})
    new_coins = info_after_buy.json()["coins"]
    assert new_coins == initial_coins - 20