from unittest.mock import MagicMock

import pytest
from fastapi.exceptions import RequestValidationError
from odmantic import ObjectId

from books_reviewing.exceptions import ObjectNotFoundException
from books_reviewing.models import Author
from books_reviewing.repositories.authors import AuthorsRepository
from books_reviewing.schemas.base import SortEnum
from books_reviewing.schemas.authors import (
    BaseAuthorSchema,
    AuthorPatchSchema,
    AuthorFilterEnum,
    AuthorOutSchema,
)
from books_reviewing.services.authors import AuthorsService
from books_reviewing.services.books import BooksService


@pytest.fixture
def mock_authors_repository():
    return MagicMock(spec=AuthorsRepository)


@pytest.fixture
def mock_books_service():
    return MagicMock(spec=BooksService)


@pytest.fixture
def authors_service(mock_authors_repository, mock_books_service):
    return AuthorsService(
        authors_repository=mock_authors_repository, books_service=mock_books_service
    )


author_data_list = [
    {"name": "John Doe", "bio": "GREAT BIO!!!"},
    {"name": "Jane Doe", "bio": "EVEN GREATER BIO"},
]

author_data = {"name": "John Doe", "bio": "GREAT BIO!!!"}

author_id = "5f85f36d6dfecacc68428a46"


@pytest.mark.asyncio
async def test_create_author(authors_service, mock_authors_repository):
    base_author_schema = BaseAuthorSchema(**author_data)

    mock_authors_repository.save.return_value = Author(
        **author_data, id=ObjectId(author_id)
    )

    created_author = await authors_service.create(base_author_schema)

    mock_authors_repository.save.assert_called_once()
    assert isinstance(created_author, Author)
    assert created_author.name == author_data["name"]


@pytest.mark.asyncio
async def test_update_author(authors_service, mock_authors_repository):
    author_patch_schema = AuthorPatchSchema(**author_data)

    mock_authors_repository.get_one.return_value = Author(
        name="Old John", bio="old bio (he was young and foolish)", id=author_id
    )
    mock_authors_repository.save.return_value = Author(**author_data)

    updated_author = await authors_service.update(
        ObjectId(author_id), author_patch_schema
    )

    mock_authors_repository.get_one.assert_called_once_with(ObjectId(author_id))
    mock_authors_repository.save.assert_called_once()
    assert isinstance(updated_author, Author)
    assert updated_author.name == author_data["name"]
    assert str(updated_author.id) == author_id


@pytest.mark.asyncio
async def test_get_one_author(
    authors_service, mock_authors_repository, mock_books_service
):
    mock_authors_repository.get_one.return_value = Author(**author_data, id=author_id)

    retrieved_author = await authors_service.get_one(ObjectId(author_id))

    mock_authors_repository.get_one.assert_called_once_with(ObjectId(author_id))
    mock_books_service.get_book_count_for_author.assert_called_once_with(
        ObjectId(author_id)
    )
    assert isinstance(retrieved_author, AuthorOutSchema)
    assert retrieved_author.name == author_data["name"]
    assert str(retrieved_author.id) == author_id


@pytest.mark.asyncio
async def test_query_filters(authors_service, mock_authors_repository):
    mock_authors_repository.query.return_value = [
        Author(**data) for data in author_data_list if data["name"] == "John Doe"
    ]

    result = await authors_service.query(
        filter_attributes=[AuthorFilterEnum.name, AuthorFilterEnum.bio],
        filter_values=["John Doe", "the great bio"],
    )

    mock_authors_repository.query.assert_called_once_with(
        filters_dict={"name": "John Doe", "bio": "the great bio"},
        sort=AuthorFilterEnum.name,
        sort_direction=SortEnum.asc,
        page=1,
        size=10,
    )
    assert isinstance(result, list)
    assert all(isinstance(author, Author) for author in result)
    assert all(author.name in ["John Doe"] for author in result)


@pytest.mark.asyncio
async def test_query_default(authors_service, mock_authors_repository):
    mock_authors_repository.query.return_value = [
        Author(**data) for data in author_data_list
    ]

    result = await authors_service.query()

    mock_authors_repository.query.assert_called_once_with(
        filters_dict={},
        sort=AuthorFilterEnum.name,
        sort_direction=SortEnum.asc,
        page=1,
        size=10,
    )
    assert isinstance(result, list)
    assert all(isinstance(author, Author) for author in result)
    assert all(author.name in ["John Doe", "Jane Doe"] for author in result)


@pytest.mark.asyncio
async def test_query_sort(authors_service, mock_authors_repository):
    mock_authors_repository.query.return_value = [
        Author(**data) for data in author_data_list
    ]

    result = await authors_service.query(
        sort=AuthorFilterEnum.bio, sort_direction=SortEnum.desc
    )

    mock_authors_repository.query.assert_called_once_with(
        filters_dict={},
        sort=AuthorFilterEnum.bio,
        sort_direction=SortEnum.desc,
        page=1,
        size=10,
    )
    assert isinstance(result, list)
    assert all(isinstance(author, Author) for author in result)
    assert all(author.name in ["John Doe", "Jane Doe"] for author in result)


@pytest.mark.asyncio
async def test_wrong_filters(authors_service, mock_authors_repository):
    with pytest.raises(RequestValidationError):
        await authors_service.query(
            filter_attributes=[AuthorFilterEnum.name, AuthorFilterEnum.bio],
            filter_values=["John Doe"],
        )


@pytest.mark.asyncio
async def test_delete_author(
    authors_service, mock_authors_repository, mock_books_service
):
    mock_authors_repository.get_one.return_value = Author(
        name="Old John", bio="too old now"
    )

    await authors_service.delete(ObjectId(author_id))

    mock_authors_repository.get_one.assert_called_once_with(ObjectId(author_id))
    mock_authors_repository.delete.assert_called_once()
    mock_books_service.delete_books_for_author.assert_called_once_with(
        ObjectId(author_id)
    )


@pytest.mark.asyncio
async def test_delete_author_not_found(authors_service, mock_authors_repository):
    mock_authors_repository.get_one.return_value = None

    with pytest.raises(ObjectNotFoundException):
        await authors_service.delete(ObjectId(author_id))

    mock_authors_repository.get_one.assert_called_once_with(ObjectId(author_id))
    mock_authors_repository.delete.assert_not_called()


@pytest.mark.asyncio
async def test_patch_author_not_found(authors_service, mock_authors_repository):
    mock_authors_repository.get_one.return_value = None

    with pytest.raises(ObjectNotFoundException):
        await authors_service.update(ObjectId(author_id), AuthorPatchSchema(name="kkk"))

    mock_authors_repository.get_one.assert_called_once_with(ObjectId(author_id))
    mock_authors_repository.delete.assert_not_called()
