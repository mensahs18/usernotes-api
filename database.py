from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DB_URL = "sqlite:///./notes.db"

engine = create_engine(DB_URL, echo=True)

LocalSession = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

    