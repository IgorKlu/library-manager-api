import os

import pytest

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.db_models.user_model import UserModel
from app.services.library_db_service import LibraryDBService
from app.db_models.book_copy_model import BookCopyModel

# Database integration tests require DATABASE_URL
pytestmark = pytest.mark.skipif(
    os.getenv("DATABASE_URL") is None,
    reason="DATABASE_URL is not set"
)

def test_create_user_adds_user_to_database():
    db = SessionLocal()
    service = LibraryDBService()
    user = None

    try:
        user = service.create_user(db, "Test", "User")

        assert user.id
        assert user.name == "Test"
        assert user.surname == "User"

        saved_user = db.get(UserModel, user.id)

        assert saved_user is not None
        assert saved_user.id == user.id
        assert saved_user.name == user.name
        assert saved_user.surname == user.surname


    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()

def test_create_book_adds_book_and_copies_to_database():
    db = SessionLocal()
    service = LibraryDBService()
    book = None
    copies = []

    try:
        book = service.create_book(db, "Steve Jobs", "Walter Isaacson")

        assert book.id
        assert book.title == "Steve Jobs"
        assert book.author == "Walter Isaacson"

        copies_statement = select(BookCopyModel).where(BookCopyModel.book_id == book.id)
        copies = db.execute(copies_statement).scalars().all()

        assert len(copies) == 1
        assert all(copy.book_id == book.id for copy in copies)
        assert all(not copy.is_borrowed for copy in copies)

    finally:
        try:
            if book is not None:
                copies_statement = select(BookCopyModel).where(BookCopyModel.book_id == book.id)
                copies_to_delete = db.execute(copies_statement).scalars().all()

                for copy in copies_to_delete:
                    db.delete(copy)

                db.delete(book)
                db.commit()

        finally:
            db.close()