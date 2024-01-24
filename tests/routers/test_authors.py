from unittest.mock import MagicMock

import pytest as pytest
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from odmantic import ObjectId

from dependencies import get_authors_service
from exceptions import ObjectNotFoundException
from main import app
from models import Author
from schemas.base import SortEnum
from schemas.authors import BaseAuthorSchema, AuthorPatchSchema, AuthorFilterEnum, AuthorOutSchema
from services.authors import AuthorsService

test_author_data = {
    "name": "John Doe",
    "bio": "The Great John",
}

test_author_id = "5f85f36d6dfecacc68428a46"

add_pagination(app)


@pytest.mark.asyncio
async def test_create_author():
    client = TestClient(app)
    mock_authors_service = MagicMock(spec=AuthorsService)
    app.dependency_overrides[get_authors_service] = lambda: mock_authors_service

    author_data = test_author_data

    mock_authors_service.create.return_value = Author(**author_data, id=ObjectId(test_author_id))

    response = client.post("/api/v1/authors/", json=author_data)

    mock_authors_service.create.assert_called_once_with(BaseAuthorSchema(**author_data))
    assert response.status_code == 200
    assert author_data.items() <= response.json().items()
    assert response.json()['id'] is not None


def test_update_author_when_missing():
    client = TestClient(app)
    mock_authors_service = MagicMock(spec=AuthorsService)
    app.dependency_overrides[get_authors_service] = lambda: mock_authors_service

    author_id = test_author_id
    author_data = test_author_data

    mock_authors_service.update.side_effect = ObjectNotFoundException(detail="Author not found")

    response = client.patch(f"/api/v1/authors/{author_id}", json=author_data)

    mock_authors_service.update.assert_called_once_with(ObjectId(author_id), AuthorPatchSchema(**author_data))
    assert response.status_code == 404


def test_update_author():
    client = TestClient(app)
    mock_authors_service = MagicMock(spec=AuthorsService)
    app.dependency_overrides[get_authors_service] = lambda: mock_authors_service

    author_id = test_author_id
    author_data = test_author_data

    mock_authors_service.update.return_value = Author(**author_data, id=ObjectId(author_id))

    response = client.patch(f"/api/v1/authors/{author_id}", json=author_data)

    mock_authors_service.update.assert_called_once_with(ObjectId(author_id), AuthorPatchSchema(**author_data))
    assert response.status_code == 200
    assert author_data.items() <= response.json().items()
    assert response.json()['id'] == author_id


def test_get_one_author_when_missing():
    client = TestClient(app)
    mock_authors_service = MagicMock(spec=AuthorsService)
    app.dependency_overrides[get_authors_service] = lambda: mock_authors_service

    mock_authors_service.get_one.side_effect = ObjectNotFoundException(detail="Author not found")

    response = client.get(f"/api/v1/authors/{test_author_id}")

    mock_authors_service.get_one.assert_called_once_with(ObjectId(test_author_id))
    assert response.status_code == 404


def test_get_one_author():
    client = TestClient(app)
    mock_authors_service = MagicMock(spec=AuthorsService)
    app.dependency_overrides[get_authors_service] = lambda: mock_authors_service

    author_data = test_author_data
    books_count = 53

    mock_authors_service.get_one.return_value = AuthorOutSchema(**author_data, id=ObjectId(test_author_id),
                                                                books_count=books_count)

    response = client.get(f"/api/v1/authors/{test_author_id}")

    mock_authors_service.get_one.assert_called_once_with(ObjectId(test_author_id))
    assert response.status_code == 200
    print(response.json())
    assert response.json()['id'] == test_author_id
    assert response.json()['books_count'] == books_count

def test_query_authors_with_filters_and_sort():
    client = TestClient(app)
    mock_authors_service = MagicMock(spec=AuthorsService)
    app.dependency_overrides[get_authors_service] = lambda: mock_authors_service

    filter_attributes = [AuthorFilterEnum.name, AuthorFilterEnum.bio]
    filter_values = ["John Doe", "JohN The GREAT"]
    sort = AuthorFilterEnum.bio
    sort_direction = SortEnum.desc

    mock_authors_service.query.return_value = ([Author(**test_author_data, id=ObjectId(test_author_id))], 1)

    response = client.get(
        f"/api/v1/authors/?filter_attributes={filter_attributes[0].lower()}"
        f"&filter_attributes={filter_attributes[1].lower()}"
        f"&filter_values={filter_values[0]}&filter_values={filter_values[1]}"
        f"&sort={sort.lower()}&sort_direction={sort_direction.lower()}"
    )

    expected_sort = AuthorFilterEnum.bio
    expected_sort_direction = SortEnum.desc

    mock_authors_service.query.assert_called_once_with(
        filter_attributes,
        filter_values,
        expected_sort,
        expected_sort_direction,
        None,
        None
    )
    assert response.status_code == 200
    response_json_items = response.json()['items']
    assert test_author_data.items() <= response_json_items[0].items()
    assert test_author_id == response_json_items[0]['id']


def test_delete_author():
    client = TestClient(app)
    mock_authors_service = MagicMock(spec=AuthorsService)
    app.dependency_overrides[get_authors_service] = lambda: mock_authors_service

    response = client.delete(f"/api/v1/authors/{test_author_id}")

    mock_authors_service.delete.assert_called_once_with(ObjectId(test_author_id))
    assert response.status_code == 204


def test_delete_author_not_found():
    client = TestClient(app)
    mock_authors_service = MagicMock(spec=AuthorsService)
    app.dependency_overrides[get_authors_service] = lambda: mock_authors_service

    mock_authors_service.delete.side_effect = ObjectNotFoundException(detail="Author not found")

    response = client.delete(f"/api/v1/authors/{test_author_id}")

    mock_authors_service.delete.assert_called_once_with(ObjectId(test_author_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Author not found"}
