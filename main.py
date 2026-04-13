from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

import models, schemas, crud
from database import SessionLocal, engine

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

@app.post("/trade")
def add_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    return crud.create_trade(db, trade)

@app.get("/trades")
def read_trades(db: Session = Depends(get_db)):
    return crud.get_trades(db)


@app.delete("/dev/reset-trades")
def reset_trades():
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS trades"))
    return {"message": "trades table dropped"}