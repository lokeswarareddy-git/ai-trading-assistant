from sqlalchemy.orm import Session
import models
import schemas


def calculate_pnl(side, entry_price, exit_price, quantity):

    if exit_price is None:
        return 0
    else:
        status = "CLOSED"
        if side == "BUY":
            return (exit_price - entry_price) * quantity

        elif side == "SELL":
            return (entry_price - exit_price) * quantity

def create_trade(db: Session, trade: schemas.TradeCreate):

    # 1. Calculate PnL

    #pnl = (trade.entry_price - trade.exit_price)* trade.quantity * -1

    # 2. Create the Database Model instance.
    db_trade = models.Trade(
        symbol=trade.symbol,
        side=trade.side,
        entry_price=trade.entry_price,
        exit_price=trade.exit_price,
        quantity=trade.quantity,
        strategy=trade.strategy,
        notes=trade.notes,
        pnl = calculate_pnl(
        trade.side,
        trade.entry_price,
        trade.exit_price,
        trade.quantity
    ),
    status="CLOSED" if trade.exit_price is not None else "OPEN"
    )
    #db_trade = models.Trade(**trade.dict())

    # 3. Use the Session to save
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade


def get_trades(db: Session):
    return db.query(models.Trade).order_by(models.Trade.timestamp.desc()).all()