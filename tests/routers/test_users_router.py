from fastapi import status

from fastapi.testclient import TestClient

from app.db_models.user_model import UserModel

def test_list_users_returns_users(
        client: TestClient,
        user: UserModel,
):
    list_response = client.get("/users/")

    assert list_response.status_code == status.HTTP_200_OK

    users = list_response.json()

    user_ids = [user_data["id"] for user_data in users]

    assert user.id in user_ids


def test_create_user_creates_user(
        client: TestClient,
):
    create_response = client.post(
        "/users/",
        json={
            "name": "Test",
            "surname": "User",
        }
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    user_data = create_response.json()

    assert user_data["id"]
    assert user_data["name"] == "Test"
    assert user_data["surname"] == "User"

def test_create_user_raises_409_when_user_already_exists(
        client: TestClient,
        user: UserModel,
):
    post_response = client.post(
        "/users/",
        json={
            "name": user.name,
            "surname": user.surname
        },
    )

    assert post_response.status_code == status.HTTP_409_CONFLICT
    assert post_response.json()["detail"] == "User already exists"

def test_get_user_by_id_returns_user(
    client: TestClient,
    user: UserModel,
):
    get_response = client.get(f"/users/{user.id}")

    assert get_response.status_code == status.HTTP_200_OK

    user_data = get_response.json()

    assert user_data["id"]
    assert user_data["name"] == user.name
    assert user_data["surname"] == user.surname

def test_get_user_by_id_raises_404_when_user_does_not_exist(
        client: TestClient,
):
    get_response = client.get("/users/invalid-user-id")

    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    assert get_response.json()["detail"] == "User not found"

def test_search_users_returns_users_list(
        client: TestClient,
        user: UserModel,
):
    get_response = client.get(
        "/users/search",
        params={
            "name": user.name,
            "surname": user.surname,
        },
    )

    assert get_response.status_code == status.HTTP_200_OK

    users = get_response.json()

    user_ids = [user_data["id"] for user_data in users]

    assert user.id in user_ids

def test_list_user_active_borrowings_returns_borrowings_list(
        client: TestClient,
        user: UserModel,
        borrowed_copy: dict,
):
    get_response = client.get(
        f"/users/{user.id}/borrowings/active"
    )

    assert get_response.status_code == status.HTTP_200_OK

    user_borrowings = get_response.json()

    borrowing: dict | None = next(
        (
        borrowing_data
        for borrowing_data in user_borrowings
        if borrowing_data["book_copy_id"] == borrowed_copy["id"]
        ),
        None,
    )

    assert borrowing is not None
    assert borrowing["user_id"] == user.id
    assert borrowing["book_copy_id"] == borrowed_copy["id"]
    assert borrowing["returned_at"] is None

def test_list_user_active_borrowing_raises_404_when_user_does_not_exist(
        client: TestClient
):
    get_response = client.get("users/invalid-user-id/borrowings/active")

    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    assert get_response.json()["detail"] == "User not found"
