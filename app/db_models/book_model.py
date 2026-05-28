from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from app.database.base import Base


class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    author: Mapped[str] = mapped_column(String(1000), nullable=False)
