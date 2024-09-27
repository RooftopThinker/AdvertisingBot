import sqlalchemy
from .database import SqlAlchemyBase


class Service(SqlAlchemyBase):
    __tablename__ = 'servíces'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    category = sqlalchemy.Column(sqlalchemy.Integer)
    name = sqlalchemy.Column(sqlalchemy.String)
    message_id = sqlalchemy.Column(sqlalchemy.BigInteger)
    chat_id = sqlalchemy.Column(sqlalchemy.BigInteger)

