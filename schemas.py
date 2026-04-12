from pydantic import BaseModel
class TradeCreate(BaseModel):
    symbol: str
    entry_price: float
    exit_price: float
    quantity: int
    stratagy: str
    notes: str
