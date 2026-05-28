from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from app.database.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(70), nullable=False)
    surname: Mapped[str] = mapped_column(String(70), nullable=False)

