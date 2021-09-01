import fastapi_users as fastusr
from app.db.base_class import Base


class UserTable(Base, fastusr.db.SQLAlchemyBaseUserTable):
    pass
