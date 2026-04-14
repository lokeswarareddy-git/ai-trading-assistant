from pydantic import BaseModel
from datetime import datetime



class TradeCreate(BaseModel):
    symbol: str
    side: str
    strategy: str
    entry_price: float
    exit_price: float
    quantity: int
    strategy: str
    notes: str


class TradeOut(BaseModel):
    id: int
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    quantity: int
    strategy: str | None
    notes: str | None
    pnl: float | None   # 👈 MUST ADD THIS
    timestamp: datetime
    class Config:
        from_attributes = True  # for SQLAlchemy