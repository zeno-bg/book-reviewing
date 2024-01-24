import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.exceptions import RequestValidationError
from odmantic import ObjectId

from exceptions import ObjectNotFoundException
from models import Book
from repositories.books import BooksRepository
from schemas.base import SortEnum
from schemas.books import BaseBookSchema, BookPatchSchema, BookFilterEnum
from services.authors import AuthorsService
from services.books import BooksService


@pytest.fixture
def mock_books_repository():
    return MagicMock(spec=BooksRepository)


@pytest.fixture
def mock_authors_service():
    return MagicMock(spec=AuthorsService)


@pytest.fixture
def books_service(mock_books_repository, mock_authors_service):
    return BooksService(books_repository=mock_books_repository, authors_service=mock_authors_service)

author_id = '5f85f36d6dfecacc68428a26'
book_data_list = [
    {"title": "John Doe Forever", "publication_date": "2024-01-23T21:19:18.307552", "isbn": "1111112121",
     "description": "John Doe rules the world", "author_id": author_id},
    {"title": "John Doe Unstoppable", "publication_date": "2024-01-23T21:19:18.307552", "isbn": "1111112122",
     "description": "John Doe goes on", "author_id": author_id},
]

book_data = {
    "title": "John Doe Forever",
    "publication_date": "2024-01-23T21:19:18.307552",
    "isbn": "1111112121",
    "description": "John Doe rules the world",
    "author_id": author_id
}

book_id = '5f85f36d6dfecacc68428a26'


@pytest.mark.asyncio
async def test_create_book(books_service, mock_books_repository, mock_authors_service):
    base_book_schema = BaseBookSchema(**book_data)

    mock_books_repository.save.return_value = Book(**book_data)

    created_book = await books_service.create(base_book_schema)

    mock_books_repository.save.assert_called_once()
    mock_authors_service.get_one.assert_called_once_with(ObjectId(author_id))
    assert isinstance(created_book, Book)
    assert created_book.title == book_data["title"]


@pytest.mark.asyncio
async def test_create_book_fails_if_author_missing(books_service, mock_books_repository, mock_authors_service):
    base_book_schema = BaseBookSchema(**book_data)

    mock_books_repository.save.return_value = Book(**book_data)
    mock_authors_service.get_one.side_effect = ObjectNotFoundException(detail="Book not found")

    with pytest.raises(ObjectNotFoundException):
        await books_service.create(base_book_schema)

    mock_authors_service.get_one.assert_called_once_with(ObjectId(author_id))
    mock_books_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_update_book(books_service, mock_books_repository):
    book_patch_schema = BookPatchSchema(**book_data)

    mock_books_repository.get_one.return_value = Book(title="Old John Doe", description="He's getting old",
                                                      publication_date="2024-01-23T21:19:18.307552",
                                                      isbn='21234567890',
                                                      id=book_id,
                                                      author_id=author_id)
    mock_books_repository.save.return_value = Book(**book_data)

    updated_book = await books_service.update(ObjectId(book_id), book_patch_schema)

    mock_books_repository.get_one.assert_called_once_with(ObjectId(book_id))
    mock_books_repository.save.assert_called_once()
    assert isinstance(updated_book, Book)
    assert updated_book.title == book_data["title"]
    assert str(updated_book.id) == book_id


@pytest.mark.asyncio
async def test_get_one_book(books_service, mock_books_repository):

    mock_books_repository.get_one.return_value = Book(**book_data, id=book_id)

    retrieved_book = await books_service.get_one(ObjectId(book_id))

    mock_books_repository.get_one.assert_called_once_with(ObjectId(book_id))
    assert isinstance(retrieved_book, Book)
    assert retrieved_book.title == book_data["title"]
    assert str(retrieved_book.id) == book_id


@pytest.mark.asyncio
async def test_query_filters(books_service, mock_books_repository):
    mock_books_repository.query.return_value = [Book(**data) for data in book_data_list if data['title'] == 'John Doe']

    result = await books_service.query(filter_attributes=[BookFilterEnum.title, BookFilterEnum.publication_date],
                                       filter_values=["John Doe", "2024-01-23T21:19:18.307552"])

    mock_books_repository.query.assert_called_once_with(
        filters_dict={'title': 'John Doe', 'publication_date': datetime.datetime.fromisoformat('2024-01-23T21:19:18.307552')},
        sort=BookFilterEnum.title,
        sort_direction=SortEnum.asc,
        page=1,
        size=10
    )
    assert isinstance(result, list)
    assert all(isinstance(book, Book) for book in result)
    assert all(book.title in ["John Doe"] for book in result)


@pytest.mark.asyncio
async def test_query_default(books_service, mock_books_repository):

    mock_books_repository.query.return_value = [Book(**data) for data in book_data_list]

    result = await books_service.query()

    mock_books_repository.query.assert_called_once_with(
        filters_dict={},
        sort=BookFilterEnum.title,
        sort_direction=SortEnum.asc,
        page = 1,
        size = 10
    )
    assert isinstance(result, list)
    assert all(isinstance(book, Book) for book in result)
    assert all(book.title in ["John Doe Forever", "John Doe Unstoppable"] for book in result)

@pytest.mark.asyncio
async def test_query_sort(books_service, mock_books_repository):
    mock_books_repository.query.return_value = [Book(**data) for data in book_data_list]

    result = await books_service.query(sort=BookFilterEnum.isbn, sort_direction=SortEnum.desc)

    mock_books_repository.query.assert_called_once_with(
        filters_dict={},
        sort=BookFilterEnum.isbn,
        sort_direction=SortEnum.desc,
        page=1,
        size=10
    )
    assert isinstance(result, list)
    assert all(isinstance(book, Book) for book in result)
    assert all(book.title in ["John Doe Forever", "John Doe Unstoppable"] for book in result)


@pytest.mark.asyncio
async def test_wrong_filters(books_service, mock_books_repository):
    with pytest.raises(RequestValidationError):
        await books_service.query(filter_attributes=[BookFilterEnum.title, BookFilterEnum.isbn], filter_values=["John Doe"])


@pytest.mark.asyncio
async def test_delete_book(books_service, mock_books_repository):
    mock_books_repository.get_one.return_value = Book(title="Too old", description="old@mail.com",
                                                      publication_date="2024-01-23T21:19:18.307552", isbn='21234567890',
                                                      author_id=author_id)

    await books_service.delete(ObjectId(book_id))

    mock_books_repository.get_one.assert_called_once_with(ObjectId(book_id))
    mock_books_repository.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_book_not_found(books_service, mock_books_repository):
    mock_books_repository.get_one.return_value = None

    with pytest.raises(ObjectNotFoundException):
        await books_service.delete(ObjectId(book_id))

    mock_books_repository.get_one.assert_called_once_with(ObjectId(book_id))
    mock_books_repository.delete.assert_not_called()


@pytest.mark.asyncio
async def test_patch_book_not_found(books_service, mock_books_repository):
    mock_books_repository.get_one.return_value = None

    with pytest.raises(ObjectNotFoundException):
        await books_service.update(ObjectId(book_id), BookPatchSchema(title="kkk"))

    mock_books_repository.get_one.assert_called_once_with(ObjectId(book_id))
    mock_books_repository.delete.assert_not_called()
