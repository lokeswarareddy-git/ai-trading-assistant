from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String, index=True)
    side = Column(String, nullable=False)       # BUY / SELL
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    entry_price = Column(Float)
    exit_price = Column(Float)
    quantity= Column(Integer)
    strategy = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    pnl = Column(Float)
    status = Column(String, nullable=False, default="OPEN")  # OPEN / CLOSED

