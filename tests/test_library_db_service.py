import os

import pytest

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from collections.abc import Generator

from app.db_models.user_model import UserModel
from app.services.library_db_service import LibraryDBService
from app.db_models.book_copy_model import BookCopyModel
from app.db_models.book_model import BookModel
from app.database.connection import engine
from app.exceptions import (
    BookNotFoundError,
    UserNotFoundError,
    BookCopyNotFoundError,
    BorrowingNotFoundError,
    BookIsBorrowedError,
)

from app.db_models.borrowing_model import BorrowingModel

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

@pytest.fixture
def user(db_session: Session, service: LibraryDBService) -> UserModel:
    return service.create_user(
        db=db_session,
        name="Test",
        surname="User",
    )

@pytest.fixture
def book(db_session: Session, service: LibraryDBService) -> BookModel:
    return service.create_book(
        db=db_session,
        title="Steve Jobs",
        author="Walter Isaacson",
    )

@pytest.fixture
def book_with_three_copies(db_session: Session, service: LibraryDBService) -> BookModel:
    return service.create_book(
        db=db_session,
        title="Steve Jobs",
        author="Walter Isaacson",
        copies_count=3
    )

@pytest.fixture
def borrowed_copy(
        db_session: Session,
        service: LibraryDBService,
        book: BookModel,
        user: UserModel,
) -> BookCopyModel:
    return service.borrow_book(
        db=db_session,
        user_id=user.id,
        book_id=book.id,
    )

@pytest.fixture
def returned_copy(
        db_session: Session,
        service: LibraryDBService,
        user: UserModel,
        borrowed_copy: BookCopyModel
) -> BookCopyModel:
    return service.return_book_copy(
        db=db_session,
        user_id=user.id,
        copy_id=borrowed_copy.id,
    )

def test_create_user_adds_user_to_database(
        db_session: Session,
        service: LibraryDBService
):
    user = service.create_user(
        db=db_session,
        name="Test",
        surname="User",
    )

    assert user.id
    assert user.name == "Test"
    assert user.surname == "User"

    saved_user = db_session.get(UserModel, user.id)

    assert saved_user is not None
    assert saved_user.id == user.id
    assert saved_user.name == user.name
    assert saved_user.surname == user.surname

def test_create_book_adds_book_and_copies_to_database(
        db_session: Session,
        service: LibraryDBService
):
    book = service.create_book(
        db=db_session,
        title="Steve Jobs",
        author="Walter Isaacson",
    )

    assert book.id
    assert book.title == "Steve Jobs"
    assert book.author == "Walter Isaacson"

    copies_statement = select(BookCopyModel).where(BookCopyModel.book_id == book.id)
    copies = db_session.execute(copies_statement).scalars().all()

    assert len(copies) == 1
    assert all(copy.book_id == book.id for copy in copies)
    assert all(not copy.is_borrowed for copy in copies)

def test_list_books_returns_created_books(
        db_session: Session,
        service: LibraryDBService,
        book: BookModel,
):
        book_2 = service.create_book(
            db=db_session,
            title="The Big Short",
            author="Michael Lewis"
        )

        books = service.list_books(db_session)
        book_ids = [book.id for book in books]

        assert book.id in book_ids
        assert book_2.id in book_ids

def test_list_users_returns_created_users(
        db_session: Session,
        service: LibraryDBService,
        user: UserModel,
):
    user_2 = service.create_user(
        db=db_session,
        name="Test2",
        surname="User2"
    )

    users = service.list_users(db_session)
    user_ids = [user.id for user in users]

    assert user.id in user_ids
    assert user_2.id in user_ids

def test_get_book_by_id_returns_book(
        db_session: Session,
        service: LibraryDBService,
        book: BookModel
):
    found_book = service.get_book_by_id(
        db=db_session,
        book_id=book.id,

    )
    assert found_book.id == book.id
    assert found_book.title == book.title
    assert found_book.author == book.author

def test_get_book_by_id_raises_error_when_book_doesnt_exists(
        db_session: Session,
        service: LibraryDBService,
):
    with pytest.raises(BookNotFoundError) as error:
        service.get_book_by_id(
            db=db_session,
            book_id="Invalid-book-ID"
        )

    assert str(error.value) == "Book not found"

def test_get_user_by_id_returns_user(
        db_session: Session,
        service: LibraryDBService,
        user: UserModel,
):
    found_user = service.get_user_by_id(
        db=db_session,
        user_id=user.id,
    )

    assert found_user.id == user.id
    assert found_user.name == user.name
    assert found_user.surname == user.surname

def test_get_user_by_id_raises_error_when_user_doesnt_exists(
        db_session: Session,
        service: LibraryDBService,
):
    with pytest.raises(UserNotFoundError) as error:
        service.get_user_by_id(
            db=db_session,
            user_id="Invalid-user-ID"
        )

    assert str(error.value) == "User not found"

def test_find_book_copy_by_id(db_session: Session, service: LibraryDBService):
    book = service.create_book(
        db=db_session,
        title="Steve Jobs",
        author="Walter Isaacson",
    )

    copies = service.find_copies_for_book(
        db=db_session,
        book_id=book.id
    )

    created_copy = copies[0]

    book_copy = service.get_book_copy_by_id(
        db=db_session,
        copy_id=created_copy.id,
    )

    assert book_copy.id == created_copy.id
    assert book_copy.book_id == book.id
    assert not book_copy.is_borrowed

def test_find_book_copy_by_id_raises_error_when_copy_does_not_exists(
        db_session: Session,
        service: LibraryDBService
):
    with pytest.raises(BookCopyNotFoundError) as error:
        service.get_book_copy_by_id(
            db=db_session,
            copy_id="Invalid-book-copy-ID"
        )

def test_find_copies_for_book_returns_book_copies(
        db_session: Session,
        service: LibraryDBService,
        book_with_three_copies: BookModel,
):
    copies = service.find_copies_for_book(
        db=db_session,
        book_id=book_with_three_copies.id,
    )

    assert len(copies) == 3
    assert all(copy.book_id == book_with_three_copies.id for copy in copies)
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
        book: BookModel,
):
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

def test_borrow_book_marks_copy_as_borrowed_and_creates_borrowing(
        db_session: Session,
        user: UserModel,
        book: BookModel,
        borrowed_copy: BookCopyModel,
):
    assert borrowed_copy.id
    assert borrowed_copy.book_id == book.id
    assert borrowed_copy.is_borrowed is True

    statement = select(BorrowingModel).where(
        BorrowingModel.book_copy_id == borrowed_copy.id,
        BorrowingModel.user_id == user.id,
        BorrowingModel.returned_at.is_(None),
    )

    borrowing: BorrowingModel | None = db_session.scalars(statement).first()

    assert borrowing is not None
    assert borrowing.user_id  == user.id
    assert borrowing.book_copy_id == borrowed_copy.id
    assert borrowing.returned_at is None

def test_borrow_book_raises_book_copy_not_found_when_no_copy_is_available(
        db_session: Session,
        service: LibraryDBService,
        user: UserModel,
        book: BookModel,
        borrowed_copy: BookCopyModel,
):
    with pytest.raises(BookCopyNotFoundError) as error:
        service.borrow_book(
            db=db_session,
            user_id=user.id,
            book_id=book.id,
        )

    assert str(error.value) == "No available copy"

def test_return_book_marks_copy_as_not_borrowed_and_sets_returned_at(
        db_session: Session,
        user: UserModel,
        book: BookModel,
        borrowed_copy: BookCopyModel,
        returned_copy: BookCopyModel,
):
    assert returned_copy.id == borrowed_copy.id
    assert returned_copy.book_id == book.id
    assert returned_copy.is_borrowed is False

    statement = select(BorrowingModel).where(
        BorrowingModel.user_id == user.id,
        BorrowingModel.book_copy_id == returned_copy.id,
    )

    borrowing: BorrowingModel | None = db_session.scalars(statement).one_or_none()

    assert borrowing is not None
    assert borrowing.user_id == user.id
    assert borrowing.book_copy_id == returned_copy.id
    assert borrowing.returned_at is not None

def test_return_book_raises_borrowing_not_found_error_when_user_has_no_active_borrowings(
        db_session: Session,
        service: LibraryDBService,
        user: UserModel,
        book: BookModel,
):
    copies = service.find_copies_for_book(
        db=db_session,
        book_id=book.id
    )

    book_copy = copies[0]

    with pytest.raises(BorrowingNotFoundError) as error:
        service.return_book_copy(
            db=db_session,
            user_id=user.id,
            copy_id=book_copy.id,
        )

    assert str(error.value) == "Borrowing not found"

def test_remove_book_deletes_book_and_its_copies(
        db_session: Session,
        service: LibraryDBService,
        book: BookModel,
):
    copies = service.find_copies_for_book(
        db=db_session,
        book_id=book.id
    )

    removed_book = service.remove_book(
        db=db_session,
        book_id=book.id
    )

    assert removed_book.id == book.id

    with pytest.raises(BookNotFoundError):
        service.get_book_by_id(
            db=db_session,
            book_id=book.id
        )

    for book_copy in copies:
        with pytest.raises(BookCopyNotFoundError):
            service.get_book_copy_by_id(
                db=db_session,
                copy_id=book_copy.id,
            )

def test_remove_book_raises_error_when_book_copy_is_borrowed(
        db_session:  Session,
        service: LibraryDBService,
        book: BookModel,
        user: UserModel,
        borrowed_copy: BookCopyModel,
):
    with pytest.raises(BookIsBorrowedError) as error:
        service.remove_book(
            db=db_session,
            book_id=book.id
        )

    assert str(error.value) == "Book has borrowed copies"

def test_search_books_returns_matching_books_by_title(
    db_session: Session,
    service: LibraryDBService,
    book: BookModel,
):
    search_results = service.search_books(
        db=db_session,
        title=book.title,
    )

    found_book = next(
        (
            searched_book
            for searched_book in search_results
            if searched_book.id == book.id
        ),
        None,
    )

    assert found_book is not None
    assert found_book.id == book.id
    assert found_book.title == book.title
    assert found_book.author == book.author

def test_search_user_returns_matching_users_by_name(
    db_session: Session,
    service: LibraryDBService,
    user: UserModel,
):
    search_results = service.search_users(
        db=db_session,
        name=user.name,
    )

    found_user = next(
        (
            searched_user
            for searched_user in search_results
            if searched_user.id == user.id
        ),
        None,
    )

    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.name == user.name
    assert found_user.surname == user.surname

def test_list_user_borrowings_returns_active_borrowings(
        db_session: Session,
        service: LibraryDBService,
        book: BookModel,
        user: UserModel,
        borrowed_copy: BorrowingModel,
):
    active_borrowings = service.list_user_active_borrowings(
        db=db_session,
        user_id=user.id
    )

    borrowing = next(
        active_borrowing
        for active_borrowing in active_borrowings
        if active_borrowing.book_copy_id == borrowed_copy.id
    )

    assert borrowing is not None
    assert borrowing.user_id == user.id
    assert borrowing.book_copy_id == borrowed_copy.id
    assert borrowing.returned_at is None

def test_list_user_borrowings_does_not_returns_returned_borrowings(
        db_session: Session,
        service: LibraryDBService,
        book: BookModel,
        user: UserModel,
        returned_copy: BookCopyModel,
):
    active_borrowings = service.list_user_active_borrowings(
        db=db_session,
        user_id=user.id
    )

    active_borrowed_copy_ids = [
        borrowing.book_copy_id
        for borrowing in active_borrowings
    ]

    assert returned_copy.id not in active_borrowed_copy_ids