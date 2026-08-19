import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("'DATABASE_URL' environment variable is not set.")

DB_URL: str = DATABASE_URL

engine = create_async_engine(DB_URL)

LocalSession = async_sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
