from sqlalchemy.orm import Session
import models 

def create_trade(db: Session, trade):

    # 1. Calculate PnL

    pnl = (trade.entry_price - trade.exit_price)* trade.quantity * -1

    # 2. Create the Database Model instance
    db_trade = models.Trade(
        symbol=trade.symbol,
        entry_price=trade.entry_price,
        exit_price=trade.exit_price,
        quantity=trade.quantity,
        stratagy=trade.stratagy,
        notes=trade.notes,
        pnl=pnl
    )

    # 3. Use the Session to save
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade


def get_trades(db: Session):
    return db.query(models.Trade).all()