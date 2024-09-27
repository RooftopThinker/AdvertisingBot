import sqlalchemy
from .database import SqlAlchemyBase


class AboutMaster(SqlAlchemyBase):
    __tablename__ = 'about_master'
    name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    message_id = sqlalchemy.Column(sqlalchemy.BigInteger)
    chat_id = sqlalchemy.Column(sqlalchemy.BigInteger)
