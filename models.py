from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from database import Base

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    side = Column(String, nullable=False)       # BUY / SELL
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    entry_price = Column(Float)
    exit_price = Column(Float)
    quantity= Column(Integer)
    strategy = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    pnl = Column(Float)

