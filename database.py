from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DB_URL = "sqlite+aiosqlite:///./notes.db"

engine = create_async_engine(DB_URL)

LocalSession = async_sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
