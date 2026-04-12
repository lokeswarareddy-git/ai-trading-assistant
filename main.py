from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import models, schemas, crud
from database import SessionLocal, engine

# ✅ THIS LINE MUST RUN ON STARTUP
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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