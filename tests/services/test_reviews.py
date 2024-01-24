import datetime
from copy import copy
from unittest.mock import MagicMock

import pytest
from fastapi.exceptions import RequestValidationError
from odmantic import ObjectId

from exceptions import ObjectNotFoundException
from models import Review
from repositories.reviews import ReviewsRepository
from schemas.base import SortEnum
from schemas.reviews import BaseReviewSchema, ReviewPatchSchema, ReviewFilterEnum
from services.books import BooksService
from services.users import UsersService
from services.reviews import ReviewsService


@pytest.fixture
def mock_reviews_repository():
    return MagicMock(spec=ReviewsRepository)


@pytest.fixture
def mock_books_service():
    return MagicMock(spec=BooksService)


@pytest.fixture
def mock_users_service():
    return MagicMock(spec=UsersService)


@pytest.fixture
def reviews_service(mock_reviews_repository, mock_books_service, mock_users_service):
    return ReviewsService(
        reviews_repository=mock_reviews_repository,
        books_service=mock_books_service,
        users_service=mock_users_service,
    )


user_1_id = "5f85f36d6dfecacc68228a26"
user_2_id = "5f85f36d6dfecacc68328a27"

book_1_id = "5f85f36d6dfecacc68428a26"
book_2_id = "5f85f36d6dfecacc68428a16"
review_data_list = [
    {
        "rating": 1,
        "comment": "The book was too heavy",
        "book_id": book_1_id,
        "user_id": user_1_id,
    },
    {
        "rating": 4,
        "comment": "The book was a PDF....",
        "book_id": book_1_id,
        "user_id": user_2_id,
    },
    {
        "rating": 2,
        "comment": "Not my favorite!",
        "book_id": book_2_id,
        "user_id": user_1_id,
    },
    {"rating": 3, "comment": "What?", "book_id": book_2_id, "user_id": user_2_id},
    {"rating": 5, "comment": "It's great", "book_id": book_2_id, "user_id": user_2_id},
]

review_data = {
    "rating": 1,
    "comment": "The book was too heavy",
    "book_id": book_1_id,
    "user_id": user_1_id,
}

review_id = "5f85f36d6dfecacc68428a26"


@pytest.mark.asyncio
async def test_create_review(
    reviews_service, mock_reviews_repository, mock_books_service, mock_users_service
):
    base_review_schema = BaseReviewSchema(**review_data)

    mock_reviews_repository.save.return_value = Review(**review_data)

    created_review = await reviews_service.create(base_review_schema)

    mock_reviews_repository.save.assert_called_once()
    mock_books_service.get_one_without_rating.assert_called_once_with(
        ObjectId(review_data["book_id"])
    )
    mock_users_service.get_one.assert_called_once_with(ObjectId(review_data["user_id"]))
    assert isinstance(created_review, Review)
    assert created_review.comment == review_data["comment"]


@pytest.mark.asyncio
async def test_create_review_fails_if_book_missing(
    reviews_service, mock_reviews_repository, mock_books_service
):
    base_review_schema = BaseReviewSchema(**review_data)

    mock_reviews_repository.save.return_value = Review(**review_data)
    mock_books_service.get_one_without_rating.side_effect = ObjectNotFoundException(
        detail="Book not found"
    )

    with pytest.raises(ObjectNotFoundException):
        await reviews_service.create(base_review_schema)

    mock_books_service.get_one_without_rating.assert_called_once_with(
        ObjectId(review_data["book_id"])
    )
    mock_reviews_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_update_review(
    reviews_service, mock_reviews_repository, mock_books_service, mock_users_service
):
    patch_data = copy(review_data)
    patch_data["comment"] = "I changed my mind"
    patch_data["user_id"] = user_2_id
    patch_data["book_id"] = book_2_id
    review_patch_schema = ReviewPatchSchema(**patch_data)

    mock_reviews_repository.get_one.return_value = Review(**review_data, id=review_id)
    mock_reviews_repository.save.return_value = Review(
        **review_patch_schema.model_dump()
    )

    updated_review = await reviews_service.update(
        ObjectId(review_id), review_patch_schema
    )

    mock_reviews_repository.get_one.assert_called_once_with(ObjectId(review_id))
    mock_books_service.get_one_without_rating.assert_called_once_with(
        ObjectId(review_patch_schema.book_id)
    )
    mock_users_service.get_one.assert_called_once_with(
        ObjectId(review_patch_schema.user_id)
    )
    mock_reviews_repository.save.assert_called_once()
    assert isinstance(updated_review, Review)
    assert updated_review.comment == review_patch_schema.comment
    assert str(updated_review.id) == review_id


@pytest.mark.asyncio
async def test_update_review_with_same_book_and_user(
    reviews_service, mock_reviews_repository, mock_books_service, mock_users_service
):
    patch_data = copy(review_data)
    patch_data["comment"] = "Updated comment"
    review_patch_schema = ReviewPatchSchema(**patch_data)

    mock_reviews_repository.get_one.return_value = Review(**review_data, id=review_id)
    mock_reviews_repository.save.return_value = Review(
        **review_patch_schema.model_dump()
    )

    updated_review = await reviews_service.update(
        ObjectId(review_id), review_patch_schema
    )

    mock_reviews_repository.get_one.assert_called_once_with(ObjectId(review_id))
    mock_books_service.get_one_without_rating.assert_not_called()
    mock_users_service.get_one.assert_not_called()
    mock_reviews_repository.save.assert_called_once()
    assert isinstance(updated_review, Review)
    assert updated_review.comment == review_patch_schema.comment
    assert str(updated_review.id) == review_id


@pytest.mark.asyncio
async def test_update_review_with_invalid_book_and_user(
    reviews_service, mock_reviews_repository, mock_books_service, mock_users_service
):
    patch_data = copy(review_data)
    patch_data["comment"] = "Updated comment"
    patch_data["user_id"] = user_2_id
    patch_data["book_id"] = book_2_id
    review_patch_schema = ReviewPatchSchema(**patch_data)

    mock_reviews_repository.get_one.return_value = Review(**review_data, id=review_id)
    mock_books_service.get_one_without_rating.side_effect = ObjectNotFoundException(
        "nmot found"
    )
    mock_users_service.get_one.side_effect = ObjectNotFoundException("nmot found")

    with pytest.raises(ObjectNotFoundException):
        await reviews_service.update(ObjectId(review_id), review_patch_schema)

    mock_reviews_repository.get_one.assert_called_once_with(ObjectId(review_id))
    mock_books_service.get_one_without_rating.assert_called_once_with(
        ObjectId(review_patch_schema.book_id)
    )
    mock_users_service.get_one.assert_called_once_with(
        ObjectId(review_patch_schema.user_id)
    )
    mock_reviews_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_get_one_review(
    reviews_service, mock_reviews_repository, mock_users_service
):
    mock_reviews_repository.get_one.return_value = Review(
        **review_data, id=ObjectId(review_id)
    )

    retrieved_review = await reviews_service.get_one(ObjectId(review_id))

    mock_reviews_repository.get_one.assert_called_once_with(ObjectId(review_id))
    assert isinstance(retrieved_review, Review)
    assert retrieved_review.comment == review_data["comment"]
    assert str(retrieved_review.id) == review_id


@pytest.mark.asyncio
async def test_query_filters(reviews_service, mock_reviews_repository):
    mock_reviews_repository.query.return_value = [
        Review(**data) for data in review_data_list
    ]

    result = await reviews_service.query(
        filter_attributes=[ReviewFilterEnum.book_id, ReviewFilterEnum.rating],
        filter_values=[book_1_id, 2],
    )

    mock_reviews_repository.query.assert_called_once_with(
        filters_dict={"book_id": ObjectId(book_1_id), "rating": 2},
        sort=ReviewFilterEnum.comment,
        sort_direction=SortEnum.asc,
        page=1,
        size=10,
    )
    assert isinstance(result, list)
    assert all(isinstance(review, Review) for review in result)


@pytest.mark.asyncio
async def test_query_default(reviews_service, mock_reviews_repository):
    mock_reviews_repository.query.return_value = [
        Review(**data) for data in review_data_list
    ]

    result = await reviews_service.query()

    mock_reviews_repository.query.assert_called_once_with(
        filters_dict={},
        sort=ReviewFilterEnum.comment,
        sort_direction=SortEnum.asc,
        page=1,
        size=10,
    )
    assert isinstance(result, list)
    assert all(isinstance(review, Review) for review in result)


@pytest.mark.asyncio
async def test_query_sort(reviews_service, mock_reviews_repository):
    mock_reviews_repository.query.return_value = [
        Review(**data) for data in review_data_list
    ]

    result = await reviews_service.query(
        sort=ReviewFilterEnum.rating, sort_direction=SortEnum.desc
    )

    mock_reviews_repository.query.assert_called_once_with(
        filters_dict={},
        sort=ReviewFilterEnum.rating,
        sort_direction=SortEnum.desc,
        page=1,
        size=10,
    )
    assert isinstance(result, list)
    assert all(isinstance(review, Review) for review in result)


@pytest.mark.asyncio
async def test_wrong_filters(reviews_service, mock_reviews_repository):
    with pytest.raises(RequestValidationError):
        await reviews_service.query(
            filter_attributes=[ReviewFilterEnum.comment, ReviewFilterEnum.rating],
            filter_values=["John Doe"],
        )


@pytest.mark.asyncio
async def test_delete_review(
    reviews_service, mock_reviews_repository, mock_users_service
):
    mock_reviews_repository.get_one.return_value = Review(
        **review_data_list[0], id=ObjectId(review_id)
    )

    await reviews_service.delete(ObjectId(review_id))

    mock_reviews_repository.get_one.assert_called_once_with(ObjectId(review_id))
    mock_reviews_repository.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_review_not_found(reviews_service, mock_reviews_repository):
    mock_reviews_repository.get_one.return_value = None

    with pytest.raises(ObjectNotFoundException):
        await reviews_service.delete(ObjectId(review_id))

    mock_reviews_repository.get_one.assert_called_once_with(ObjectId(review_id))
    mock_reviews_repository.delete.assert_not_called()


@pytest.mark.asyncio
async def test_patch_review_not_found(reviews_service, mock_reviews_repository):
    mock_reviews_repository.get_one.return_value = None

    with pytest.raises(ObjectNotFoundException):
        await reviews_service.update(
            ObjectId(review_id), ReviewPatchSchema(comment="kkk")
        )

    mock_reviews_repository.get_one.assert_called_once_with(ObjectId(review_id))
    mock_reviews_repository.delete.assert_not_called()


@pytest.mark.asyncio
async def test_get_average_rating_for_book(reviews_service, mock_reviews_repository):
    mock_reviews_repository.get_average_rating_for_book.return_value = 3.14
    result = await reviews_service.get_average_rating_for_book(ObjectId(book_1_id))
    mock_reviews_repository.get_average_rating_for_book.assert_called_once_with(
        ObjectId(book_1_id)
    )
    assert result == 3.14


@pytest.mark.asyncio
async def test_delete_reviews_for_book(reviews_service, mock_reviews_repository):
    await reviews_service.delete_reviews_for_book(ObjectId(book_1_id))
    mock_reviews_repository.delete_reviews_for_book.assert_called_once_with(
        ObjectId(book_1_id)
    )


@pytest.mark.asyncio
async def test_delete_reviews_for_books(reviews_service, mock_reviews_repository):
    await reviews_service.delete_reviews_for_books(
        [ObjectId(book_1_id), ObjectId(book_2_id)]
    )
    mock_reviews_repository.delete_reviews_for_books.assert_called_once_with(
        [ObjectId(book_1_id), ObjectId(book_2_id)]
    )


@pytest.mark.asyncio
async def test_delete_reviews_for_user(reviews_service, mock_reviews_repository):
    await reviews_service.delete_reviews_by_user(ObjectId(user_1_id))
    mock_reviews_repository.delete_reviews_by_user.assert_called_once_with(
        ObjectId(user_1_id)
    )
