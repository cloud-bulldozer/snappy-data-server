import asyncio
import functools
import logging

import app.db.base as base
import app.models as mdl
import databases
import fastapi_users as fastusr
import sqlalchemy as sqa
from app.main import DATABASE_URL, env

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def async_adapter(wrapped_func):
    @functools.wraps(wrapped_func)
    def run_sync(*args, **kwargs):
        loop = asyncio.new_event_loop()
        task = wrapped_func(*args, **kwargs)
        return loop.run_until_complete(task)

    return run_sync


def create_db(db_url):
    engine = sqa.create_engine(db_url)
    base.Base.metadata.create_all(engine)


@async_adapter
async def seed_users(db_url) -> None:
    """Seed db with a users"""

    database = databases.Database(db_url)
    await database.connect()

    user_db = fastusr.db.SQLAlchemyUserDatabase(
        user_db_model=mdl.UserDB, database=database, users=base.UserTable.__table__
    )

    su = mdl.UserDB(
        email=env("FIRST_SUPERUSER"),
        hashed_password=fastusr.password.get_password_hash(env("FIRST_SUPERUSER_PASSWORD")),
        is_superuser=True,
    )
    user = await user_db.get_by_email(su.email)
    if not user:
        await user_db.create(su)

    await database.disconnect()


def main() -> None:
    logger.info("Create relations by name, if they don't exist")
    create_db(DATABASE_URL)
    logger.info("Seeding initial data")
    seed_users(DATABASE_URL)
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
