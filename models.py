from database import Base
from uuid6 import UUID, uuid7
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid7()))
    username: Mapped[str] = mapped_column(unique=True)
    fname: Mapped[str] = mapped_column()
    sname: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, " 
            f"username={self.username!r}, "
            f"firstname={self.fname!r}, "
            f"surname={self.sname!r}"
        )
    
class Note(Base):
    __tablename__ = "notes"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid7()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return (
            f"Note(id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"title={self.title!r})"
        )
