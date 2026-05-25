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

def test_create_book_raises_409_when_user_already_exists(
        client: TestClient,
        book: BookModel,
):
    post_response = client.post(
        "/books/",
        json={
            "title": book.title,
            "author": book.author,
        },
    )

    assert post_response.status_code == status.HTTP_409_CONFLICT
    assert post_response.json()["detail"] == "Book already exists"

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

def test_get_book_by_id_endpoint_returns_404_when_book_does_not_exist(
        client: TestClient
):
    get_response = client.get("/books/invalid-user-id")

    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    assert get_response.json()["detail"] == "Book not found"

def test_find_copies_for_book_returns_copies(
        client: TestClient,
        book: BookModel,
):
    get_response = client.get(f"/books/{book.id}/copies")

    assert get_response.status_code == status.HTTP_200_OK

    book_copies = get_response.json()

    assert len(book_copies) == 1
    assert book_copies[0]["book_id"] == book.id
    assert book_copies[0]["is_borrowed"] is False

def test_get_book_copy_by_id_returns_book_copy(
        client: TestClient,
        book: BookModel,
):
    copies_response = client.get(f"/books/{book.id}/copies/")

    assert copies_response.status_code == status.HTTP_200_OK

    copies = copies_response.json()
    book_copy = copies[0]

    get_response = client.get(f"books/copies/{book_copy['id']}")

    assert get_response.status_code == status.HTTP_200_OK

    book_copy_data = get_response.json()

    assert book_copy_data["id"] == book_copy["id"]
    assert book_copy_data["book_id"] == book.id
    assert book_copy_data["is_borrowed"] is False

def test_get_book_copy_by_id_raises_404_when_copy_does_not_exist(
        client: TestClient
):
    get_response = client.get("/books/copies/invalid-copy-id")

    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    assert get_response.json()["detail"] == "Book copy not found"

def test_add_book_copy_adds_book_copy_to_existing_book(
        client: TestClient,
        book: BookModel,
):
    post_response = client.post(f"/books/{book.id}/copies")

    assert post_response.status_code == status.HTTP_201_CREATED

    created_copy = post_response.json()

    assert created_copy["id"]
    assert created_copy["book_id"] == book.id
    assert created_copy["is_borrowed"] is False

def test_add_book_copy_raises_404_when_book_does_not_exist(
        client: TestClient
):
    post_response = client.post("books/invalid-book-id/copies")

    assert post_response.status_code == status.HTTP_404_NOT_FOUND
    assert post_response.json()["detail"] == "Book not found"
