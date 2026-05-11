from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models.user_model import UserModel
from app.db_models.book_model import BookModel
from app.db_models.book_copy_model import BookCopyModel

from app.exceptions import (
    UserAlreadyExistsError,
    BookAlreadyExistsError
)
from app.utils.id_generator import generate_id


class LibraryDBService:
    def __init__(self, id_generator: Callable[[], str] = generate_id) -> None:
        self.id_generator = id_generator

    def create_user(self, db: Session, name: str, surname: str) -> UserModel:
        statement = select(UserModel).where(
            UserModel.name == name,
            UserModel.surname == surname,
        )

        existing_user = db.execute(statement).scalar_one_or_none()

        if existing_user is not None:
            raise UserAlreadyExistsError("User already exists")

        user = UserModel(
            id=self.id_generator(),
            name=name,
            surname=surname,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    def create_book(self, db: Session, title: str, author: str, copies_count: int = 1) -> BookModel:
        if copies_count < 1:
            raise ValueError("Copies count must be greater or equal 1")

        statement = select(BookModel).where(
            BookModel.title == title,
            BookModel.author == author,
        )

        existing_book = db.execute(statement).scalar_one_or_none()

        if existing_book is not None:
            raise BookAlreadyExistsError("Book already exists")

        book = BookModel(
            id=self.id_generator(),
            title=title,
            author=author
        )

        db.add(book)
        db.flush()

        for _ in range(copies_count):
            book_copy = BookCopyModel(
                id=self.id_generator(),
                book_id=book.id,
            )
            db.add(book_copy)

        db.commit()
        db.refresh(book)

        return book