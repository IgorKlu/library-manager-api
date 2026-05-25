from fastapi import status
from fastapi.testclient import TestClient

from app.db_models.user_model import UserModel
from app.db_models.book_model import BookModel

def test_borrow_book_borrows_book(
    client: TestClient,
    user: UserModel,
    book: BookModel,
):
    borrow_response = client.post(
        "/borrowings/",
        json={
            "user_id": user.id,
            "book_id": book.id
        },
    )

    assert borrow_response.status_code == status.HTTP_201_CREATED

    borrowed_copy = borrow_response.json()

    assert borrowed_copy["id"]
    assert borrowed_copy["book_id"] == book.id
    assert borrowed_copy["is_borrowed"] is True

def test_borrow_book_raises_404_when_user_does_not_exist(
        client: TestClient,
        book: BookModel,
):
    borrow_response = client.post(
        "/borrowings/",
        json={
            "user_id": "invalid-user-id",
            "book_id": book.id
        },
    )

    assert borrow_response.status_code == status.HTTP_404_NOT_FOUND
    assert borrow_response.json()["detail"] == "User not found"

def test_borrow_book_raises_404_when_book_does_not_exist(
        client: TestClient,
        user: UserModel,
):
    borrow_response = client.post(
        "/borrowings/",
        json={
            "user_id": user.id,
            "book_id": "invalid-book-id",
        },
    )

    assert borrow_response.status_code == status.HTTP_404_NOT_FOUND
    assert borrow_response.json()["detail"] == "Book not found"

def test_borrow_book_raises_409_when_copy_is_not_available(
        client: TestClient,
        user: UserModel,
        book: BookModel,
):
    first_response = client.post(
        "/borrowings/",
        json={
            "user_id": user.id,
            "book_id": book.id,
        },
    )

    assert first_response.status_code == status.HTTP_201_CREATED

    second_response = client.post(
        "/borrowings/",
        json={
            "user_id": user.id,
            "book_id": book.id,
        },
    )

    assert second_response.status_code == status.HTTP_409_CONFLICT
    assert second_response.json()["detail"] == "No available copy"

def test_return_book_copy_returns_book_copy(
        client: TestClient,
        book: BookModel,
        user: UserModel,
        borrowed_copy: dict,
):
    return_response = client.post(
        "/borrowings/return/",
        json={
            "user_id": user.id,
            "copy_id": borrowed_copy["id"]
        },
    )

    assert return_response.status_code == status.HTTP_201_CREATED

    return_data = return_response.json()

    assert return_data["id"] == borrowed_copy["id"]
    assert return_data["book_id"] == borrowed_copy["book_id"]
    assert return_data["is_borrowed"] is False

def test_return_book_raises_404_when_user_does_not_exists(
        client: TestClient,
        book: BookModel,
        borrowed_copy: dict,
):
    return_response = client.post(
        "/borrowings/return",
        json={
            "user_id": "invalid-user-id",
            "copy_id": book.id
        },
    )

    assert return_response.status_code == status.HTTP_404_NOT_FOUND
    assert return_response.json()["detail"] == "User not found"

def test_return_book_raises_404_when_book_copy_does_not_exists(
        client: TestClient,
        user: UserModel,
        borrowed_copy: dict,
):
    return_response = client.post(
        "/borrowings/return",
        json={
            "user_id": user.id,
            "copy_id": "invalid-book-id",
        },
    )

    assert return_response.status_code == status.HTTP_404_NOT_FOUND
    assert return_response.json()["detail"] == "Book copy not found"

def test_return_book_raises_404_when_borrowing_does_not_exist(
        client: TestClient,
        user: UserModel,
        book: BookModel,
):
    copies_response = client.get(f"/books/{book.id}/copies")

    assert copies_response.status_code == status.HTTP_200_OK

    copies = copies_response.json()

    book_copy = copies[0]

    return_response = client.post(
        "/borrowings/return",
        json={
            "user_id": user.id,
            "copy_id": book_copy["id"],
        },
    )

    assert return_response.status_code == status.HTTP_404_NOT_FOUND
    assert return_response.json()["detail"] == "Borrowing not found"