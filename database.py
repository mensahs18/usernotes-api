import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DB_URL)

LocalSession = async_sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
