import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.exceptions import RequestValidationError
from odmantic import ObjectId

from books_reviewing.exceptions import ObjectNotFoundException
from books_reviewing.models import User
from books_reviewing.repositories.users import UsersRepository
from books_reviewing.schemas.base import SortEnum
from books_reviewing.schemas.users import BaseUserSchema, UserPatchSchema, UserFilterEnum
from books_reviewing.services.reviews import ReviewsService
from books_reviewing.services.users import UsersService


@pytest.fixture
def mock_users_repository():
    return MagicMock(spec=UsersRepository)


@pytest.fixture
def mock_reviews_service():
    return MagicMock(spec=ReviewsService)


@pytest.fixture
def users_service(mock_users_repository, mock_reviews_service):
    return UsersService(
        users_repository=mock_users_repository, reviews_service=mock_reviews_service
    )


user_data_list = [
    {
        "name": "John Doe",
        "birthday": "2024-01-23T21:19:18.307552",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
    },
    {
        "name": "Jane Doe",
        "birthday": "2024-01-23T21:19:18.307552",
        "email": "jane.doe@example.com",
        "phone": "+9876543210",
    },
]

user_data = {
    "name": "John Doe",
    "birthday": "2024-01-23T21:19:18.307552",
    "email": "john@doe.com",
    "phone": "+1234567890",
}

user_id = "5f85f36d6dfecacc68428a46"


@pytest.mark.asyncio
async def test_create_user(users_service, mock_users_repository):
    base_user_schema = BaseUserSchema(**user_data)

    mock_users_repository.save.return_value = User(**user_data)

    created_user = await users_service.create(base_user_schema)

    mock_users_repository.save.assert_called_once()
    assert isinstance(created_user, User)
    assert created_user.name == user_data["name"]


@pytest.mark.asyncio
async def test_update_user(users_service, mock_users_repository):
    user_patch_schema = UserPatchSchema(**user_data)

    mock_users_repository.get_one.return_value = User(
        name="Old Name",
        email="old@mail.com",
        birthday="2024-01-23T21:19:18.307552",
        phone="+1234567890",
        id=user_id,
    )
    mock_users_repository.save.return_value = User(**user_data)

    updated_user = await users_service.update(ObjectId(user_id), user_patch_schema)

    mock_users_repository.get_one.assert_called_once_with(ObjectId(user_id))
    mock_users_repository.save.assert_called_once()
    assert isinstance(updated_user, User)
    assert updated_user.name == user_data["name"]
    assert str(updated_user.id) == user_id


@pytest.mark.asyncio
async def test_get_one_user(users_service, mock_users_repository):
    mock_users_repository.get_one.return_value = User(**user_data, id=user_id)

    retrieved_user = await users_service.get_one(ObjectId(user_id))

    mock_users_repository.get_one.assert_called_once_with(ObjectId(user_id))
    assert isinstance(retrieved_user, User)
    assert retrieved_user.name == user_data["name"]
    assert str(retrieved_user.id) == user_id


@pytest.mark.asyncio
async def test_query_filters(users_service, mock_users_repository):
    mock_users_repository.query.return_value = [
        User(**data) for data in user_data_list if data["name"] == "John Doe"
    ]

    result = await users_service.query(
        filter_attributes=[UserFilterEnum.name, UserFilterEnum.birthday],
        filter_values=["John Doe", "2024-01-23T21:19:18.307552"],
    )

    mock_users_repository.query.assert_called_once_with(
        filters_dict={
            "name": "John Doe",
            "birthday": datetime.datetime.fromisoformat("2024-01-23T21:19:18.307552"),
        },
        sort=UserFilterEnum.name,
        sort_direction=SortEnum.asc,
        page=1,
        size=10,
    )
    assert isinstance(result, list)
    assert all(isinstance(user, User) for user in result)
    assert all(user.name in ["John Doe"] for user in result)


@pytest.mark.asyncio
async def test_query_default(users_service, mock_users_repository):
    mock_users_repository.query.return_value = [User(**data) for data in user_data_list]

    result = await users_service.query()

    mock_users_repository.query.assert_called_once_with(
        filters_dict={},
        sort=UserFilterEnum.name,
        sort_direction=SortEnum.asc,
        page=1,
        size=10,
    )
    assert isinstance(result, list)
    assert all(isinstance(user, User) for user in result)
    assert all(user.name in ["John Doe", "Jane Doe"] for user in result)


@pytest.mark.asyncio
async def test_query_sort(users_service, mock_users_repository):
    mock_users_repository.query.return_value = [User(**data) for data in user_data_list]

    result = await users_service.query(
        sort=UserFilterEnum.email, sort_direction=SortEnum.desc
    )

    mock_users_repository.query.assert_called_once_with(
        filters_dict={},
        sort=UserFilterEnum.email,
        sort_direction=SortEnum.desc,
        page=1,
        size=10,
    )
    assert isinstance(result, list)
    assert all(isinstance(user, User) for user in result)
    assert all(user.name in ["John Doe", "Jane Doe"] for user in result)


@pytest.mark.asyncio
async def test_wrong_filters(users_service, mock_users_repository):
    with pytest.raises(RequestValidationError):
        await users_service.query(
            filter_attributes=[UserFilterEnum.name, UserFilterEnum.birthday],
            filter_values=["John Doe"],
        )


@pytest.mark.asyncio
async def test_delete_user(users_service, mock_users_repository, mock_reviews_service):
    mock_users_repository.get_one.return_value = User(
        name="Old Name",
        email="old@mail.com",
        birthday="2024-01-23T21:19:18.307552",
        phone="+1234567890",
    )

    await users_service.delete(ObjectId(user_id))

    mock_reviews_service.delete_reviews_by_user.assert_called_once_with(
        ObjectId(user_id)
    )
    mock_users_repository.get_one.assert_called_once_with(ObjectId(user_id))
    mock_users_repository.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_not_found(users_service, mock_users_repository):
    mock_users_repository.get_one.return_value = None

    with pytest.raises(ObjectNotFoundException):
        await users_service.delete(ObjectId(user_id))

    mock_users_repository.get_one.assert_called_once_with(ObjectId(user_id))
    mock_users_repository.delete.assert_not_called()


@pytest.mark.asyncio
async def test_patch_user_not_found(users_service, mock_users_repository):
    mock_users_repository.get_one.return_value = None

    with pytest.raises(ObjectNotFoundException):
        await users_service.update(ObjectId(user_id), UserPatchSchema(name="kkk"))

    mock_users_repository.get_one.assert_called_once_with(ObjectId(user_id))
    mock_users_repository.delete.assert_not_called()
