from database import Base
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    fname: Mapped[str] = mapped_column()
    sname: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, firstname={self.fname!r}, surname={self.sname!r}, password={self.password!r})"
    