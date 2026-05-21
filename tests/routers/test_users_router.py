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
