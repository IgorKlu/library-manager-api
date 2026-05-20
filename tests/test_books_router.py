from collections.abc import Generator

import pytest

from fastapi.testclient import TestClient

from app.main import app

from sqlalchemy.orm import Session, sessionmaker
from app.database.connection import engine, get_db
from app.services.library_db_service import LibraryDBService

from app.db_models.book_model import BookModel

@pytest.fixture
def service() -> LibraryDBService:
    return LibraryDBService()

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()

    TestSessionLocal = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        join_transaction_mode="create_savepoint"
    )

    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()

@pytest.fixture
def book(db_session: Session, service: LibraryDBService) -> BookModel:
    return service.create_book(
        db=db_session,
        title="Steve Jobs",
        author="Walter Isaacson",
    )

def test_list_books_endpoint_returns_books(
        client: TestClient,
        book: BookModel,
):
    response = client.get("/books/")

    assert response.status_code == 200

    books = response.json()
    book_ids = [book_data["id"] for book_data in books]

    assert book.id in book_ids
