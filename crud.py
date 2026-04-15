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

def create_trade(db: Session, trade: schemas.TradeCreate, user_id: int):

    # 1. Calculate PnL

    #pnl = (trade.entry_price - trade.exit_price)* trade.quantity * -1

    # 2. Create the Database Model instance.
    db_trade = models.Trade(
        user_id=user_id,
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


def get_trades(db: Session, user_id: int):
    return db.query(models.Trade)\
        .filter(models.Trade.user_id == user_id)\
        .order_by(models.Trade.timestamp.desc())\
        .all()


def update_trade(db: Session, trade_id: int, updates: schemas.TradeUpdate):

    db_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()

    if not db_trade:
        return None

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_trade, key, value)

    # recompute PnL if prices exist
    if db_trade.entry_price and db_trade.exit_price:
        db_trade.pnl = calculate_pnl(
            db_trade.side,
            db_trade.entry_price,
            db_trade.exit_price,
            db_trade.quantity
        )

    db.commit()
    db.refresh(db_trade)
    return db_trade


def close_trade(db: Session, trade_id: int, exit_price: float):

    db_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()

    if not db_trade:
        return None

    db_trade.exit_price = exit_price
    db_trade.status = "CLOSED"

    db_trade.pnl = calculate_pnl(
        db_trade.side,
        db_trade.entry_price,
        db_trade.exit_price,
        db_trade.quantity
    )

    db.commit()
    db.refresh(db_trade)
    return db_trade