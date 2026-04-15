from fastapi import FastAPI, Depends, HTTPException
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List
import models, schemas, crud, auth
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


@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    try:
        new_user = models.User(
            email=user.email,
            password=auth.hash_password(user.password)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created", "user_id": new_user.id}

@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email")

    if not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {
        "user_id": db_user.id,
        "email": db_user.email
    }

recent_requests = {}
@app.post("/trade", response_model=schemas.TradeOut)
def add_trade(
    user_id: int,
    trade: schemas.TradeCreate,
    request: Request, #adding to fix host issue
    db: Session = Depends(get_db)):
    ip = request.client.host
    now = time.time()

    if ip in recent_requests:
        if now - recent_requests[ip] < 2:
            raise HTTPException(status_code=429, detail="Too many requests")
    recent_requests[ip] = now
    return crud.create_trade(db, trade, user_id)

@app.get("/trades", response_model=List[schemas.TradeOut])
def read_trades(user_id: int, db: Session = Depends(get_db)):
    return crud.get_trades(db, user_id)

@app.delete("/dev/reset-trades")
def reset_trades():
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS trades"))
    return {"message": "trades table dropped"}

@app.delete("/dev/reset-users")
def reset_users():
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users"))
    return {"message": "users table dropped"}

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

@app.put("/trade/{trade_id}")
def edit_trade(
    trade_id: int,
    updates: schemas.TradeUpdate,
    db: Session = Depends(get_db)
):
    result = crud.update_trade(db, trade_id, updates)

    if not result:
        raise HTTPException(status_code=404, detail="Trade not found")

    return result


@app.post("/trade/{trade_id}/close")
def close_trade_endpoint(
    trade_id: int,
    payload: schemas.CloseTrade,
    db: Session = Depends(get_db)
):
    result = crud.close_trade(db, trade_id, payload.exit_price)

    if not result:
        raise HTTPException(status_code=404, detail="Trade not found")

    return result