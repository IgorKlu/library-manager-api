import os

import pytest

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from collections.abc import Generator

from app.db_models.user_model import UserModel
from app.services.library_db_service import LibraryDBService
from app.db_models.book_copy_model import BookCopyModel
from app.database.connection import engine
from app.exceptions import BookNotFoundError

# Database integration tests require DATABASE_URL
pytestmark = pytest.mark.skipif(
    os.getenv("DATABASE_URL") is None,
    reason="DATABASE_URL is not set"
)

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()

    TestSessionLocal = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        join_transaction_mode="create_savepoint",
    )

    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def service() -> LibraryDBService:
    return LibraryDBService()

def test_create_user_adds_user_to_database(db_session: Session, service: LibraryDBService):
    user = service.create_user(db=db_session, name="Test", surname="User")

    assert user.id
    assert user.name == "Test"
    assert user.surname == "User"

    saved_user = db_session.get(UserModel, user.id)

    assert saved_user is not None
    assert saved_user.id == user.id
    assert saved_user.name == user.name
    assert saved_user.surname == user.surname

def test_create_book_adds_book_and_copies_to_database(db_session: Session, service: LibraryDBService):
    book = service.create_book(db=db_session, title="Steve Jobs", author="Walter Isaacson")

    assert book.id
    assert book.title == "Steve Jobs"
    assert book.author == "Walter Isaacson"

    copies_statement = select(BookCopyModel).where(BookCopyModel.book_id == book.id)
    copies = db_session.execute(copies_statement).scalars().all()

    assert len(copies) == 1
    assert all(copy.book_id == book.id for copy in copies)
    assert all(not copy.is_borrowed for copy in copies)

def test_list_books_returns_created_books(db_session: Session, service: LibraryDBService):
        book_1 = service.create_book(
            db=db_session,
            title="Steve Jobs",
            author="Walter Isaacson",
        )

        book_2 = service.create_book(
            db=db_session,
            title="The Big Short",
            author="Michael Lewis"
        )

        books = service.list_books(db_session)
        book_ids = [book.id for book in books]

        assert book_1.id in book_ids
        assert book_2.id in book_ids

def test_list_users_returns_created_users(db_session: Session, service: LibraryDBService):
    user_1 = service.create_user(
        db=db_session,
        name="Test",
        surname="User"
    )

    user_2 = service.create_user(
        db=db_session,
        name="Test2",
        surname="User2"
    )

    users = service.list_users(db_session)
    user_ids = [user.id for user in users]

    assert user_1.id in user_ids
    assert user_2.id in user_ids

def test_get_book_by_id_returns_book(db_session: Session, service: LibraryDBService):
    created_book = service.create_book(
        db=db_session,
        title="Steve Jobs",
        author="Walter Isaacson",
    )

    book = service.get_book_by_id(
        db=db_session,
        book_id=created_book.id,
    )

    assert book.id == created_book.id
    assert book.title == created_book.title
    assert book.author == created_book.author

def test_get_user_by_id_returns_user(db_session: Session, service: LibraryDBService):
    created_user = service.create_user(
        db=db_session,
        name="Test",
        surname="User",
    )

    user = service.get_user_by_id(
        db=db_session,
        user_id=created_user.id,
    )

    assert user.id == created_user.id
    assert user.name == created_user.name
    assert user.surname == created_user.surname

def test_find_copies_for_book_returns_book_copies(db_session: Session, service: LibraryDBService):
    book = service.create_book(
        db=db_session,
        title="Steve Jobs",
        author="Walter Isaacson",
        copies_count=3,
    )

    copies = service.find_copies_for_book(
        db=db_session,
        book_id=book.id,
    )

    assert len(copies) == 3
    assert all(copy.book_id == book.id for copy in copies)
    assert all(not copy.is_borrowed for copy in copies)

def test_find_copies_for_book_raises_error_when_book_doesnt_exists(
        db_session: Session,
        service: LibraryDBService,
):
    with pytest.raises(BookNotFoundError) as error:
        service.find_copies_for_book(
            db=db_session,
            book_id="Invalid-book-ID"
        )

    assert str(error.value) == "Book not found"

def test_add_book_copy_ads_book_copy(
        db_session: Session,
        service: LibraryDBService,
):
    book = service.create_book(
        db=db_session,
        title="Steve Jobs",
        author="Walter Isaacson"
    )

    new_copy = service.add_book_copy(
        db=db_session,
        book_id=book.id,
    )

    assert new_copy.id
    assert new_copy.book_id == book.id
    assert not new_copy.is_borrowed

    copies = service.find_copies_for_book(
        db=db_session,
        book_id=book.id
    )

    assert len(copies) == 2