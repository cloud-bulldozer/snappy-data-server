# Import all schemas, so that Base has them before
# being imported by Alembic
from app.db.base_class import Base
from .schemas import UserTable


