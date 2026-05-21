from fastapi import status

from fastapi.testclient import TestClient

from app.db_models.book_model import BookModel

def test_list_books_endpoint_returns_books(
        client: TestClient,
        book: BookModel,
):
    list_response = client.get("/books/")

    assert list_response.status_code == status.HTTP_200_OK

    books = list_response.json()
    book_ids = [book_data["id"] for book_data in books]

    assert book.id in book_ids

def test_create_book_endpoint_creates_book(
        client: TestClient,
):
    create_response = client.post(
        "/books/",
        json={
            "title": "Steve Jobs",
            "author": "Walter Isaacson",
            "copies_count": 1,
        }
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    book_data = create_response.json()

    assert book_data["id"]
    assert book_data["title"] == "Steve Jobs"
    assert book_data["author"] == "Walter Isaacson"

def test_get_book_by_id_endpoint_returns_book(
        client: TestClient,
        book: BookModel,
):
    get_response = client.get(f"/books/{book.id}")

    assert get_response.status_code == status.HTTP_200_OK

    book_data = get_response.json()

    assert book_data["id"]
    assert book_data["title"] == book.title
    assert book_data["author"] == book.author