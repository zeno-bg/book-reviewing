from unittest.mock import MagicMock

import pytest as pytest
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from odmantic import ObjectId

from books_reviewing.dependencies import get_users_service
from books_reviewing.exceptions import ObjectNotFoundException
from books_reviewing.main import app
from books_reviewing.models import User
from books_reviewing.schemas.base import SortEnum
from books_reviewing.schemas.users import BaseUserSchema, UserPatchSchema, UserFilterEnum
from books_reviewing.services.users import UsersService

test_user_data = {
    "name": "John Doe",
    "birthday": "2024-01-23T21:19:18.307000",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
}

test_user_id = "5f85f36d6dfecacc68428a46"

add_pagination(app)


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
    assert response.json()["id"] is not None


def test_update_user_when_missing():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    user_id = "5f85f36d6dfecacc68428a46"
    user_data = test_user_data

    mock_users_service.update.side_effect = ObjectNotFoundException(
        detail="User not found"
    )

    with pytest.raises(ObjectNotFoundException):
        client.patch(f"/api/v1/users/{user_id}", json=user_data)

    mock_users_service.update.assert_called_once_with(
        ObjectId(user_id), UserPatchSchema(**user_data)
    )


def test_update_user():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    user_id = "5f85f36d6dfecacc68428a46"
    user_data = test_user_data

    mock_users_service.update.return_value = User(**user_data, id=ObjectId(user_id))

    response = client.patch(f"/api/v1/users/{user_id}", json=user_data)

    mock_users_service.update.assert_called_once_with(
        ObjectId(user_id), UserPatchSchema(**user_data)
    )
    assert response.status_code == 200
    assert user_data.items() <= response.json().items()
    assert response.json()["id"] == user_id


def test_get_one_user_when_missing():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    mock_users_service.get_one.side_effect = ObjectNotFoundException(
        detail="User not found"
    )

    with pytest.raises(ObjectNotFoundException):
        client.get(f"/api/v1/users/{test_user_id}")

    mock_users_service.get_one.assert_called_once_with(ObjectId(test_user_id))


def test_get_one_user():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    user_data = test_user_data

    mock_users_service.get_one.return_value = User(
        **user_data, id=ObjectId(test_user_id)
    )

    response = client.get(f"/api/v1/users/{test_user_id}")

    mock_users_service.get_one.assert_called_once_with(ObjectId(test_user_id))
    assert response.status_code == 200
    assert response.json()["id"] == test_user_id


def test_query_users_with_filters_and_sort():
    client = TestClient(app)
    mock_users_service = MagicMock(spec=UsersService)
    app.dependency_overrides[get_users_service] = lambda: mock_users_service

    filter_attributes = [UserFilterEnum.name, UserFilterEnum.email]
    filter_values = ["John Doe", "john.doe@example.com"]
    sort = UserFilterEnum.birthday
    sort_direction = SortEnum.desc

    mock_users_service.query.return_value = (
        [User(**test_user_data, id=ObjectId(test_user_id))],
        1,
    )

    response = client.get(
        f"/api/v1/users/?filter_attributes={filter_attributes[0].lower()}&filter_attributes={filter_attributes[1].lower()}"
        f"&filter_values={filter_values[0]}&filter_values={filter_values[1]}&sort={sort.lower()}&sort_direction={sort_direction.lower()}"
    )

    expected_sort = UserFilterEnum.birthday
    expected_sort_direction = SortEnum.desc

    mock_users_service.query.assert_called_once_with(
        filter_attributes,
        filter_values,
        expected_sort,
        expected_sort_direction,
        None,
        None,
    )
    assert response.status_code == 200
    response_json_items = response.json()["items"]
    assert test_user_data.items() <= response_json_items[0].items()
    assert test_user_id == response_json_items[0]["id"]


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

    mock_users_service.delete.side_effect = ObjectNotFoundException(
        detail="User not found"
    )

    with pytest.raises(ObjectNotFoundException):
        client.delete(f"/api/v1/users/{test_user_id}")

    mock_users_service.delete.assert_called_once_with(ObjectId(test_user_id))
