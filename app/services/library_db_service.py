from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from datetime import datetime, timezone

from app.db_models.user_model import UserModel
from app.db_models.book_model import BookModel
from app.db_models.book_copy_model import BookCopyModel

from app.exceptions import (
    UserAlreadyExistsError,
    BookAlreadyExistsError,
    BookNotFoundError,
    UserNotFoundError,
    BookCopyNotFoundError,
    BorrowingNotFoundError,
    BookIsBorrowedError,
)

from app.utils.id_generator import generate_id
from app.db_models import BorrowingModel


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

    def list_books(self, db: Session) -> list[BookModel]:
        statement = select(BookModel)
        return list(db.scalars(statement).all())

    def list_users(self, db: Session) -> list[UserModel]:
        statement = select(UserModel)
        return list(db.scalars(statement).all())

    def get_book_by_id(self, db: Session, book_id: str) -> BookModel:
        book = db.get(BookModel, book_id)

        if book is None:
            raise BookNotFoundError("Book not found")

        return book

    def get_user_by_id(self, db: Session, user_id: str) -> UserModel:
        user = db.get(UserModel, user_id)

        if user is None:
            raise UserNotFoundError("User not found")

        return user

    def get_book_copy_by_id(self, db: Session, copy_id: str) -> BookCopyModel:
        book_copy = db.get(BookCopyModel, copy_id)

        if book_copy is None:
            raise BookCopyNotFoundError("Book copy not found")

        return book_copy

    def find_copies_for_book(self, db: Session, book_id: str) -> list[BookCopyModel]:
        self.get_book_by_id(db, book_id)

        copies_statement = select(BookCopyModel).where(
            BookCopyModel.book_id == book_id
        )

        copies = list(db.scalars(copies_statement).all())

        return copies

    def add_book_copy(self, db: Session, book_id: str) -> BookCopyModel:
        book = self.get_book_by_id(db, book_id)

        book_copy = BookCopyModel(
            id=self.id_generator(),
            book_id=book_id
        )

        db.add(book_copy)
        db.commit()
        db.refresh(book_copy)

        return book_copy

    def borrow_book(self, db: Session, user_id: str, book_id: str) -> BookCopyModel:
        user = self.get_user_by_id(db, user_id)

        book = self.get_book_by_id(db, book_id)

        statement = select(BookCopyModel).where(
            BookCopyModel.book_id == book_id,
            BookCopyModel.is_borrowed.is_(False),
        )

        book_copy: BookCopyModel | None = db.scalars(statement).first()

        if book_copy is None:
            raise BookCopyNotFoundError("No available copy")

        book_copy.is_borrowed = True

        borrowing = BorrowingModel(
            id=self.id_generator(),
            user_id=user_id,
            book_copy_id=book_copy.id
        )

        db.add(borrowing)
        db.commit()
        db.refresh(book_copy)

        return book_copy

    def return_book_copy(self, db: Session, user_id: str, copy_id: str) -> BookCopyModel:
        user = self.get_user_by_id(
            db=db,
            user_id=user_id,
        )

        book_copy = self.get_book_copy_by_id(
            db=db,
            copy_id=copy_id
        )

        statement = select(BorrowingModel).where(
            BorrowingModel.user_id == user.id,
            BorrowingModel.book_copy_id == copy_id,
            BorrowingModel.returned_at.is_(None)
        )

        borrowing: BorrowingModel | None = db.scalars(statement).one_or_none()

        if borrowing is None:
            raise BorrowingNotFoundError("Borrowing not found")

        book_copy.is_borrowed = False
        borrowing.returned_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(book_copy)

        return book_copy

    def remove_book(self, db: Session, book_id: str) -> BookModel:
        book = self.get_book_by_id(
            db=db,
            book_id=book_id,
        )

        copies = self.find_copies_for_book(
            db=db,
            book_id=book_id,
        )

        if any(book_copy.is_borrowed is True for book_copy in copies):
            raise BookIsBorrowedError("Book has borrowed copies")

        for book_copy in copies:
            db.delete(book_copy)

        db.delete(book)
        db.commit()

        return book

    def search_books(
            self,
            db: Session,
            title: str | None = None,
            author: str | None = None,
    ) -> list[BookModel]:
        statement = select(BookModel)

        if title is not None:
            statement = statement.where(BookModel.title.ilike(f"%{title}%"))

        if author is not None:
            statement = statement.where(BookModel.author.ilike(f"author%"))

        return list(db.scalars(statement).all())

    def search_users(
            self,
            db: Session,
            name: str | None = None,
            surname: str | None = None,
    ) -> list[UserModel]:
        statement = select(UserModel)

        if name is not None:
            statement = statement.where(UserModel.name.ilike(f"%{name}%"))

        if surname is not None:
            statement = statement.where(UserModel.surname.ilike(f"%{surname}%"))

        return list(db.scalars(statement).all())