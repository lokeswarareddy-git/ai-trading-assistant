from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TradeCreate(BaseModel):
    symbol: str
    side: str
    strategy: str
    entry_price: float
    exit_price: Optional[float] = None
    quantity: int
    strategy: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "OPEN"


class TradeOut(BaseModel):
    id: int
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float] = None
    quantity: int
    strategy: str
    notes: str
    pnl: float  # 
    status: str
    timestamp: datetime
    class Config:
        from_attributes = True  # for SQLAlchemy