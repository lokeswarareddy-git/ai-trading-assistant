from pydantic import BaseModel
class TradeCreate(BaseModel):
    symbol: str
    entry_price: float
    exit_price: float
    quantity: int
    strategy: str
    notes: str


class TradeOut(BaseModel):
    id: int
    symbol: str
    entry_price: float
    exit_price: float
    quantity: int
    pnl: float
    strategy: str
    notes: str

    class Config:
        from_attributes = True  # for SQLAlchemy