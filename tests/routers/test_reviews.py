from unittest.mock import MagicMock

import pytest as pytest
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from odmantic import ObjectId

from dependencies import get_reviews_service
from exceptions import ObjectNotFoundException
from main import app
from models import Review
from schemas.base import SortEnum
from schemas.reviews import BaseReviewSchema, ReviewPatchSchema, ReviewFilterEnum
from services.reviews import ReviewsService

user_1_id = '5f85f36d6dfecacc68228a26'

book_1_id = '5f85f36d6dfecacc68428a26'
test_review_data = {
    "rating": 1, "comment": "The book was too heavy", 'book_id': book_1_id, 'user_id': user_1_id
}

test_review_id = "5f85f36d6dfecacc68428a26"

add_pagination(app)


@pytest.mark.asyncio
async def test_create_review():
    client = TestClient(app)
    mock_reviews_service = MagicMock(spec=ReviewsService)
    app.dependency_overrides[get_reviews_service] = lambda: mock_reviews_service

    review_data = test_review_data

    mock_reviews_service.create.return_value = Review(**review_data)

    response = client.post("/api/v1/reviews/", json=review_data)

    mock_reviews_service.create.assert_called_once_with(BaseReviewSchema(**review_data))
    assert response.status_code == 200
    assert review_data.items() <= response.json().items()
    assert response.json()['id'] is not None


def test_update_review_when_missing():
    client = TestClient(app)
    mock_reviews_service = MagicMock(spec=ReviewsService)
    app.dependency_overrides[get_reviews_service] = lambda: mock_reviews_service

    review_id = test_review_id
    review_data = test_review_data

    mock_reviews_service.update.side_effect = ObjectNotFoundException(detail="Review not found")

    response = client.patch(f"/api/v1/reviews/{review_id}", json=review_data)

    mock_reviews_service.update.assert_called_once_with(ObjectId(review_id), ReviewPatchSchema(**review_data))
    assert response.status_code == 404


def test_update_review():
    client = TestClient(app)
    mock_reviews_service = MagicMock(spec=ReviewsService)
    app.dependency_overrides[get_reviews_service] = lambda: mock_reviews_service

    review_id = test_review_id
    review_data = test_review_data

    mock_reviews_service.update.return_value = Review(**review_data, id=ObjectId(review_id))

    response = client.patch(f"/api/v1/reviews/{review_id}", json=review_data)

    mock_reviews_service.update.assert_called_once_with(ObjectId(review_id), ReviewPatchSchema(**review_data))
    assert response.status_code == 200
    assert review_data.items() <= response.json().items()
    assert response.json()['id'] == review_id


def test_get_one_review_when_missing():
    client = TestClient(app)
    mock_reviews_service = MagicMock(spec=ReviewsService)
    app.dependency_overrides[get_reviews_service] = lambda: mock_reviews_service

    mock_reviews_service.get_one.side_effect = ObjectNotFoundException(detail="Review not found")

    response = client.get(f"/api/v1/reviews/{test_review_id}")

    mock_reviews_service.get_one.assert_called_once_with(ObjectId(test_review_id))
    assert response.status_code == 404


def test_get_one_review():
    client = TestClient(app)
    mock_reviews_service = MagicMock(spec=ReviewsService)
    app.dependency_overrides[get_reviews_service] = lambda: mock_reviews_service

    review_data = test_review_data

    mock_reviews_service.get_one.return_value = Review(**review_data, id=ObjectId(test_review_id))

    response = client.get(f"/api/v1/reviews/{test_review_id}")

    mock_reviews_service.get_one.assert_called_once_with(ObjectId(test_review_id))
    assert response.status_code == 200
    assert response.json()['id'] == test_review_id

def test_query_reviews_with_filters_and_sort():
    client = TestClient(app)
    mock_reviews_service = MagicMock(spec=ReviewsService)
    app.dependency_overrides[get_reviews_service] = lambda: mock_reviews_service

    filter_attributes = [ReviewFilterEnum.rating, ReviewFilterEnum.comment]
    filter_values = ["John Doe's number one!", "23789412893471892"]
    sort = ReviewFilterEnum.rating
    sort_direction = SortEnum.desc

    mock_reviews_service.query.return_value = ([Review(**test_review_data, id=ObjectId(test_review_id))], 1)

    response = client.get(
        f"/api/v1/reviews/?filter_attributes={filter_attributes[0].lower()}"
        f"&filter_attributes={filter_attributes[1].lower()}"
        f"&filter_values={filter_values[0]}&filter_values={filter_values[1]}"
        f"&sort={sort.lower()}&sort_direction={sort_direction.lower()}"
    )

    expected_sort = ReviewFilterEnum.rating
    expected_sort_direction = SortEnum.desc

    mock_reviews_service.query.assert_called_once_with(
        filter_attributes,
        filter_values,
        expected_sort,
        expected_sort_direction,
        None,
        None
    )
    assert response.status_code == 200
    response_json_items = response.json()['items']
    assert test_review_data.items() <= response_json_items[0].items()
    assert test_review_id == response_json_items[0]['id']


def test_delete_review():
    client = TestClient(app)
    mock_reviews_service = MagicMock(spec=ReviewsService)
    app.dependency_overrides[get_reviews_service] = lambda: mock_reviews_service

    response = client.delete(f"/api/v1/reviews/{test_review_id}")

    mock_reviews_service.delete.assert_called_once_with(ObjectId(test_review_id))
    assert response.status_code == 204


def test_delete_review_not_found():
    client = TestClient(app)
    mock_reviews_service = MagicMock(spec=ReviewsService)
    app.dependency_overrides[get_reviews_service] = lambda: mock_reviews_service

    mock_reviews_service.delete.side_effect = ObjectNotFoundException(detail="Review not found")

    response = client.delete(f"/api/v1/reviews/{test_review_id}")

    mock_reviews_service.delete.assert_called_once_with(ObjectId(test_review_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Review not found"}
