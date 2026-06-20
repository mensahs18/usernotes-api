from database import Base
from uuid6 import uuid7
from sqlalchemy import ForeignKey, String, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Note(Base):
    __tablename__ = "notes"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid7()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return (
            f"Note(id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"title={self.title!r}, "
            f"content={self.content!r}, "
            f"created_at={self.created_at!r}, "
            f"updated_at={self.updated_at!r})"
        )