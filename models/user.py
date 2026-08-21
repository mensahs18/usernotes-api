from uuid import UUID

from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=lambda: uuid7())
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
