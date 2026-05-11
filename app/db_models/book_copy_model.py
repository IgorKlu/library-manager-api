from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from app.database.base import Base


class BookCopyModel(Base):
    __tablename__ = "book_copies"

    id: Mapped[str] = mapped_column(primary_key=True)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"), nullable=False)
    is_borrowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)