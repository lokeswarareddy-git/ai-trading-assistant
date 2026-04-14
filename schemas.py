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


class TradeOut(TradeCreate):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True  # for SQLAlchemy