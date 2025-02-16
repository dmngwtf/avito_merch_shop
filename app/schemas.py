from pydantic import BaseModel, Field
from typing import List, Optional


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str


class SendCoinRequest(BaseModel):
    toUser: str
    amount: int


class ErrorResponse(BaseModel):
    errors: str


class CoinHistoryItem(BaseModel):
    fromUser: Optional[str]
    toUser: Optional[str]
    amount: int


class CoinHistory(BaseModel):
    received: List[CoinHistoryItem] = []
    sent: List[CoinHistoryItem] = []


class InventoryItem(BaseModel):
    type: str
    quantity: int


class InfoResponse(BaseModel):
    coins: int
    inventory: List[InventoryItem]
    coinHistory: CoinHistory