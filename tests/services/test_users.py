from unittest.mock import MagicMock

import pytest
from odmantic import ObjectId

from exceptions import ObjectNotFoundException
from models import User
from repositories.users import UsersRepository
from schemas.users import BaseUserSchema, UserPatchSchema
from services.users import UsersService


@pytest.fixture
def mock_users_repository():
    return MagicMock(spec=UsersRepository)


@pytest.fixture
def users_service(mock_users_repository):
    return UsersService(users_repository=mock_users_repository)


@pytest.mark.asyncio
async def test_create_user(users_service, mock_users_repository):
    user_data = {
        "name": "John Doe",
        "birthday": "2024-01-23T21:19:18.307552",
        "email": "john@doe.com",
        "phone": "+1234567890",
    }
    base_user_schema = BaseUserSchema(**user_data)

    mock_users_repository.save.return_value = User(**user_data)

    created_user = await users_service.create(base_user_schema)

    mock_users_repository.save.assert_called_once()
    assert isinstance(created_user, User)
    assert created_user.name == user_data["name"]


@pytest.mark.asyncio
async def test_update_user(users_service, mock_users_repository):
    user_id = ObjectId()
    user_data = {
        "name": "Updated Name",
        "birthday": "2024-01-23T21:19:18.307552",
        "email": "updated.email@example.com",
        "phone": "+1234567890",
    }
    user_patch_schema = UserPatchSchema(**user_data)

    mock_users_repository.get_one.return_value = User(name="Old Name", email="old@mail.com",
                                                      birthday="2024-01-23T21:19:18.307552", phone='+1234567890')
    mock_users_repository.save.return_value = User(**user_data)

    updated_user = await users_service.update(user_id, user_patch_schema)

    mock_users_repository.get_one.assert_called_once_with(user_id)
    mock_users_repository.save.assert_called_once()
    assert isinstance(updated_user, User)
    assert updated_user.name == user_data["name"]


@pytest.mark.asyncio
async def test_get_one_user(users_service, mock_users_repository):
    user_id = ObjectId()
    user_data = {
        "name": "John Doe",
        "birthday": "2024-01-23T21:19:18.307552",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
    }

    mock_users_repository.get_one.return_value = User(**user_data)

    retrieved_user = await users_service.get_one(user_id)

    mock_users_repository.get_one.assert_called_once_with(user_id)
    assert isinstance(retrieved_user, User)
    assert retrieved_user.name == user_data["name"]


@pytest.mark.asyncio
async def test_get_all_users(users_service, mock_users_repository):
    user_data_list = [
        {"name": "John Doe", "birthday": "2024-01-23T21:19:18.307552", "email": "john.doe@example.com",
         "phone": "+1234567890"},
        {"name": "Jane Doe", "birthday": "2024-01-23T21:19:18.307552", "email": "jane.doe@example.com",
         "phone": "+9876543210"},
    ]

    mock_users_repository.get_all.return_value = [User(**data) for data in user_data_list]

    all_users = await users_service.get_all()

    mock_users_repository.get_all.assert_called_once()
    assert isinstance(all_users, list)
    assert all(isinstance(user, User) for user in all_users)
    assert all(user.name in ["John Doe", "Jane Doe"] for user in all_users)


@pytest.mark.asyncio
async def test_delete_user(users_service, mock_users_repository):
    user_id = ObjectId()

    mock_users_repository.get_one.return_value = User(name="Old Name", email="old@mail.com",
                                                      birthday="2024-01-23T21:19:18.307552", phone='+1234567890')

    await users_service.delete(user_id)

    mock_users_repository.get_one.assert_called_once_with(user_id)
    mock_users_repository.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_not_found(users_service, mock_users_repository):
    user_id = ObjectId()

    mock_users_repository.get_one.return_value = None

    with pytest.raises(ObjectNotFoundException):
        await users_service.delete(user_id)

    mock_users_repository.get_one.assert_called_once_with(user_id)
    mock_users_repository.delete.assert_not_called()


@pytest.mark.asyncio
async def test_patch_user_not_found(users_service, mock_users_repository):
    user_id = ObjectId()

    mock_users_repository.get_one.return_value = None

    with pytest.raises(ObjectNotFoundException):
        await users_service.update(user_id, UserPatchSchema(name="kkk"))

    mock_users_repository.get_one.assert_called_once_with(user_id)
    mock_users_repository.delete.assert_not_called()
