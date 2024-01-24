from unittest.mock import MagicMock

import pytest as pytest
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from odmantic import ObjectId

from books_reviewing.dependencies import get_books_service
from books_reviewing.exceptions import ObjectNotFoundException
from books_reviewing.main import app
from books_reviewing.models import Book
from books_reviewing.schemas.base import SortEnum
from books_reviewing.schemas.books import BaseBookSchema, BookPatchSchema, BookFilterEnum, BookOutSchema
from books_reviewing.services.books import BooksService

test_book_data = {
    "title": "John Doe's Original",
    "isbn": "23123123123",
    "description": "Truly stunning by Jown Doe",
    "publication_date": "2024-01-23T21:19:18.307000",
    "author_id": "5f85f36d6dfecacc68428a46",
}

test_book_id = "5f85f36d6dfecacc68428a26"

add_pagination(app)


@pytest.mark.asyncio
async def test_create_book():
    client = TestClient(app)
    mock_books_service = MagicMock(spec=BooksService)
    app.dependency_overrides[get_books_service] = lambda: mock_books_service

    book_data = test_book_data

    mock_books_service.create.return_value = Book(**book_data)

    response = client.post("/api/v1/books/", json=book_data)

    mock_books_service.create.assert_called_once_with(BaseBookSchema(**book_data))
    assert response.status_code == 200
    assert book_data.items() <= response.json().items()
    assert response.json()["id"] is not None


def test_update_book_when_missing():
    client = TestClient(app)
    mock_books_service = MagicMock(spec=BooksService)
    app.dependency_overrides[get_books_service] = lambda: mock_books_service

    book_id = test_book_id
    book_data = test_book_data

    mock_books_service.update.side_effect = ObjectNotFoundException(
        detail="Book not found"
    )

    with pytest.raises(ObjectNotFoundException):
        client.patch(f"/api/v1/books/{book_id}", json=book_data)

    mock_books_service.update.assert_called_once_with(
        ObjectId(book_id), BookPatchSchema(**book_data)
    )


def test_update_book():
    client = TestClient(app)
    mock_books_service = MagicMock(spec=BooksService)
    app.dependency_overrides[get_books_service] = lambda: mock_books_service

    book_id = test_book_id
    book_data = test_book_data

    mock_books_service.update.return_value = Book(**book_data, id=ObjectId(book_id))

    response = client.patch(f"/api/v1/books/{book_id}", json=book_data)

    mock_books_service.update.assert_called_once_with(
        ObjectId(book_id), BookPatchSchema(**book_data)
    )
    assert response.status_code == 200
    assert book_data.items() <= response.json().items()
    assert response.json()["id"] == book_id


def test_get_one_book_when_missing():
    client = TestClient(app)
    mock_books_service = MagicMock(spec=BooksService)
    app.dependency_overrides[get_books_service] = lambda: mock_books_service

    mock_books_service.get_one.side_effect = ObjectNotFoundException(
        detail="Book not found"
    )

    with pytest.raises(ObjectNotFoundException):
        client.get(f"/api/v1/books/{test_book_id}")

    mock_books_service.get_one.assert_called_once_with(ObjectId(test_book_id))


def test_get_one_book():
    client = TestClient(app)
    mock_books_service = MagicMock(spec=BooksService)
    app.dependency_overrides[get_books_service] = lambda: mock_books_service

    book_data = test_book_data

    mock_books_service.get_one.return_value = BookOutSchema(
        **book_data, id=ObjectId(test_book_id), average_rating=1
    )

    response = client.get(f"/api/v1/books/{test_book_id}")

    mock_books_service.get_one.assert_called_once_with(ObjectId(test_book_id))
    assert response.status_code == 200
    print(response.json())
    assert response.json()["id"] == test_book_id


def test_query_books_with_filters_and_sort():
    client = TestClient(app)
    mock_books_service = MagicMock(spec=BooksService)
    app.dependency_overrides[get_books_service] = lambda: mock_books_service

    filter_attributes = [BookFilterEnum.title, BookFilterEnum.isbn]
    filter_values = ["John Doe's number one!", "23789412893471892"]
    sort = BookFilterEnum.isbn
    sort_direction = SortEnum.desc

    mock_books_service.query.return_value = (
        [Book(**test_book_data, id=ObjectId(test_book_id))],
        1,
    )

    response = client.get(
        f"/api/v1/books/?filter_attributes={filter_attributes[0].lower()}"
        f"&filter_attributes={filter_attributes[1].lower()}"
        f"&filter_values={filter_values[0]}&filter_values={filter_values[1]}"
        f"&sort={sort.lower()}&sort_direction={sort_direction.lower()}"
    )

    expected_sort = BookFilterEnum.isbn
    expected_sort_direction = SortEnum.desc

    mock_books_service.query.assert_called_once_with(
        filter_attributes,
        filter_values,
        expected_sort,
        expected_sort_direction,
        None,
        None,
    )
    assert response.status_code == 200
    response_json_items = response.json()["items"]
    assert test_book_data.items() <= response_json_items[0].items()
    assert test_book_id == response_json_items[0]["id"]


def test_delete_book():
    client = TestClient(app)
    mock_books_service = MagicMock(spec=BooksService)
    app.dependency_overrides[get_books_service] = lambda: mock_books_service

    response = client.delete(f"/api/v1/books/{test_book_id}")

    mock_books_service.delete.assert_called_once_with(ObjectId(test_book_id))
    assert response.status_code == 204


def test_delete_book_not_found():
    client = TestClient(app)
    mock_books_service = MagicMock(spec=BooksService)
    app.dependency_overrides[get_books_service] = lambda: mock_books_service

    mock_books_service.delete.side_effect = ObjectNotFoundException(
        detail="Book not found"
    )

    with pytest.raises(ObjectNotFoundException):
        client.delete(f"/api/v1/books/{test_book_id}")

    mock_books_service.delete.assert_called_once_with(ObjectId(test_book_id))
