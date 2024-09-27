from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import DB_URL

SqlAlchemyBase = declarative_base()

engine = create_async_engine(url=DB_URL, echo=False)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)