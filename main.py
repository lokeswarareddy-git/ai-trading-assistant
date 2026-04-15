from fastapi import FastAPI, Depends, HTTPException
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List
import models, schemas, crud
from database import SessionLocal, engine
import time
# # ✅ THIS LINE MUST RUN ON STARTUP
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ BEST PRACTICE: run on startup
@app.on_event("startup")
def startup():
    models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later you can restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#Dependancy
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
recent_requests = {}
@app.post("/trade", response_model=schemas.TradeOut)
def add_trade(
    trade: schemas.TradeCreate, 
    request: Request,
    db: Session = Depends(get_db)):
    ip = request.client.host
    now = time.time()

    if ip in recent_requests:
        if now - recent_requests[ip] < 2:
            raise HTTPException(status_code=429, detail="Too many requests")
    recent_requests[ip] = now
    return crud.create_trade(db, trade)

@app.get("/trades", response_model=List[schemas.TradeOut])
def read_trades(db: Session = Depends(get_db)):
    return crud.get_trades(db)


@app.delete("/dev/reset-trades")
def reset_trades():
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS trades"))
    return {"message": "trades table dropped"}


@app.put("/trade/{trade_id}/close")
def close_trade(trade_id: int, exit_price: float, db: Session = Depends(get_db)):
    trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()

    if not trade:
        return {"error": "Trade not found"}

    trade.exit_price = exit_price
    trade.status = "CLOSED"

    if trade.side == "BUY":
        trade.pnl = (exit_price - trade.entry_price) * trade.quantity
    else:
        trade.pnl = (trade.entry_price - exit_price) * trade.quantity

    db.commit()
    db.refresh(trade)
    return trade

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):

    trades = db.query(models.Trade).all()

    total_trades = len(trades)

    if total_trades == 0:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_pnl": 0,
            "win_rate": 0
        }

    closed_trades = [t for t in trades if getattr(t, "status", "CLOSED") == "CLOSED"]

    total_pnl = sum([(t.pnl or 0) for t in closed_trades])

    winning_trades = len([t for t in closed_trades if (t.pnl or 0) > 0])
    losing_trades = len([t for t in closed_trades if (t.pnl or 0) <= 0])

    win_rate = (winning_trades / total_trades * 100) if total_trades else 0

    return {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "total_pnl": round(total_pnl, 2),
        "win_rate": round(win_rate, 2)
    }

