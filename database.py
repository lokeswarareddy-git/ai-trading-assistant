from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#DATABASE_URL = "sqlite:///./trades.db"
DATABASE_URL = "postgresql://trading_db_awmn_user:omg3kqkY9rtjpcx9ceQeyQPBLXg1FWbY@dpg-d7e01mvlk1mc73f2aju0-a/trading_db_awmn"

#engine = create_engine(DATABASE_URL, connect_args = {"check_same_thread": False}) # Commenting as we are updating as part of mysql to postgress migration
"""
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
) # adding for postgress
"""
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()
