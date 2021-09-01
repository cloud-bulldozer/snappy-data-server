import sqlalchemy as sqa
from app.main import DATABASE_URL
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=sqa.create_engine(DATABASE_URL, pool_pre_ping=True)
)
