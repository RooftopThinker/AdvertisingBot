import sqlalchemy
from .database import SqlAlchemyBase


class Document(SqlAlchemyBase):
    __tablename__ = 'documents'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    message_id = sqlalchemy.Column(sqlalchemy.BigInteger)
    chat_id = sqlalchemy.Column(sqlalchemy.BigInteger)
