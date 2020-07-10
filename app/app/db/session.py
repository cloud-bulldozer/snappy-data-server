import sqlalchemy as sqa
from sqlalchemy.orm import sessionmaker

from app.main import DATABASE_URL


SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = sqa.create_engine(
        DATABASE_URL, pool_pre_ping=True)
)