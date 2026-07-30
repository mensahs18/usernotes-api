from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


DB_URL = "sqlite+aiosqlite:///./notes.db"

engine = create_async_engine(DB_URL)

LocalSession = async_sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

    