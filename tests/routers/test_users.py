from unittest.mock import MagicMock

import pytest as pytest
from fastapi.testclient import TestClient
from odmantic import ObjectId

from dependencies import get_users_service
from exceptions import ObjectNotFoundException
from main import app
from models import User
from schemas.users import BaseUserSchema, UserPatchSchema
from services.users import UsersService

test_user_data = {
    "name": "John Doe",
    "birthday": "2024-01-23T21:19:18.307000",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
}

test_user_id = "5f85f36d6dfecacc68428a46"


@pytest.mark.asyncio
async def test_create_user():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    user_data = test_user_data

    mock_users_service.create.return_value = User(**user_data)

    response = client.post("/api/v1/users/", json=user_data)

    mock_users_service.create.assert_called_once_with(BaseUserSchema(**user_data))
    assert response.status_code == 200
    assert user_data.items() <= response.json().items()
    assert response.json()['id'] is not None


def test_update_user_when_missing():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    user_id = "5f85f36d6dfecacc68428a46"
    user_data = test_user_data

    mock_users_service.update.side_effect = ObjectNotFoundException(detail="User not found")

    response = client.patch(f"/api/v1/users/{user_id}", json=user_data)

    mock_users_service.update.assert_called_once_with(ObjectId(user_id), UserPatchSchema(**user_data))
    assert response.status_code == 404


def test_update_user():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    user_id = "5f85f36d6dfecacc68428a46"
    user_data = test_user_data

    mock_users_service.update.return_value = User(**user_data, id=ObjectId(user_id))

    response = client.patch(f"/api/v1/users/{user_id}", json=user_data)

    mock_users_service.update.assert_called_once_with(ObjectId(user_id), UserPatchSchema(**user_data))
    assert response.status_code == 200
    assert user_data.items() <= response.json().items()
    assert response.json()['id'] == user_id


def test_get_one_user_when_missing():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    mock_users_service.get_one.side_effect = ObjectNotFoundException(detail="User not found")

    response = client.get(f"/api/v1/users/{test_user_id}")

    mock_users_service.get_one.assert_called_once_with(ObjectId(test_user_id))
    assert response.status_code == 404


def test_get_one_user():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    user_data = test_user_data

    mock_users_service.get_one.return_value = User(**user_data, id=ObjectId(test_user_id))

    response = client.get(f"/api/v1/users/{test_user_id}")

    mock_users_service.get_one.assert_called_once_with(ObjectId(test_user_id))
    assert response.status_code == 200
    assert response.json()['id'] == test_user_id


def test_get_all_users_when_there_are_none():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    mock_users_service.get_all.return_value = list()

    response = client.get("/api/v1/users/")

    mock_users_service.get_all.assert_called_once()
    assert response.status_code == 200


def test_get_all_users():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    mock_users_service.get_all.return_value = list()

    response = client.get("/api/v1/users/")

    mock_users_service.get_all.assert_called_once()
    assert response.status_code == 200


def test_delete_user():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    response = client.delete(f"/api/v1/users/{test_user_id}")

    mock_users_service.delete.assert_called_once_with(ObjectId(test_user_id))
    assert response.status_code == 204


def test_delete_user_not_found():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    mock_users_service.delete.side_effect = ObjectNotFoundException(detail="User not found")

    response = client.delete(f"/api/v1/users/{test_user_id}")

    mock_users_service.delete.assert_called_once_with(ObjectId(test_user_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
