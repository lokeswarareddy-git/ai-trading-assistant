from sqlalchemy import Column, Integer, Float, String
from database import Base

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    entry_price = Column(Float)
    exit_price = Column(Float)
    quantity= Column(Integer)
    stratagy = Column(String)
    notes = Column(String)
    pnl = Column(Float)