import sqlalchemy
from .database import SqlAlchemyBase


class Admin(SqlAlchemyBase):
    __tablename__ = 'admins'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    tg_id = sqlalchemy.Column(sqlalchemy.BigInteger, unique=True, nullable=False)
    username = sqlalchemy.Column(sqlalchemy.String)
    can_promote_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_owner = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    promoted_by = sqlalchemy.Column(sqlalchemy.Integer)