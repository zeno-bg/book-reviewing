import asyncio

from fastapi.exceptions import RequestValidationError
from odmantic import ObjectId

from books_reviewing.exceptions import ObjectNotFoundException
from books_reviewing.models import Review
from books_reviewing.repositories.reviews import ReviewsRepository
from books_reviewing.schemas.base import SortEnum
from books_reviewing.schemas.reviews import (
    BaseReviewSchema,
    ReviewPatchSchema,
    ReviewFilterEnum,
)
from books_reviewing.services.books import BooksService
from books_reviewing.services.users import UsersService


class ReviewsService:
    books_service: BooksService
    users_service: UsersService

    __reviews_repository: ReviewsRepository

    def __init__(
        self,
        reviews_repository: ReviewsRepository,
        books_service: BooksService,
        users_service: UsersService,
    ):
        self.__reviews_repository = reviews_repository
        self.books_service = books_service
        self.users_service = users_service

    async def create(self, review: BaseReviewSchema) -> Review:
        await asyncio.gather(
            self.books_service.get_one_without_rating(review.book_id),
            self.users_service.get_one(review.user_id),
        )
        review_in_db = Review(**review.model_dump())
        return await self.__reviews_repository.save(review_in_db)

    async def update(
        self, review_id: ObjectId, review_new: ReviewPatchSchema
    ) -> Review:
        review = await self.__get_review_by_id_if_exists(review_id)

        tasks = []

        if review_new.book_id and review_new.book_id != review.book_id:
            tasks.append(self.books_service.get_one_without_rating(review_new.book_id))

        if review_new.user_id and review_new.user_id != review.user_id:
            tasks.append(self.users_service.get_one(review_new.user_id))

        if len(tasks) > 0:
            await asyncio.gather(*tasks)

        review.model_update(review_new, exclude_unset=True)
        await self.__reviews_repository.save(review)
        return review

    async def get_one(self, review_id: ObjectId) -> Review:
        return await self.__get_review_by_id_if_exists(review_id)

    async def query(
        self,
        filter_attributes: list[ReviewFilterEnum] = None,
        filter_values: list[str] = None,
        sort: ReviewFilterEnum = None,
        sort_direction: SortEnum = None,
        page: int = None,
        size: int = None,
    ) -> (list[Review], int):
        filters_dict = {}
        if filter_attributes and filter_values:
            if len(filter_attributes) != len(filter_values):
                raise RequestValidationError(
                    "Wrong number of filter attributes and values!"
                )
            i = 0
            for attribute in filter_attributes:
                if attribute in [ReviewFilterEnum.book_id, ReviewFilterEnum.user_id]:
                    filters_dict[attribute.lower()] = ObjectId(filter_values[i])
                else:
                    filters_dict[attribute.lower()] = filter_values[i]
                i += 1
        return await self.__reviews_repository.query(
            filters_dict=filters_dict,
            sort=sort if sort else ReviewFilterEnum.comment,
            sort_direction=sort_direction.lower() if sort_direction else "asc",
            page=page if page else 1,
            size=size if size else 10,
        )

    async def get_average_rating_for_book(self, book_id: ObjectId) -> float:
        return await self.__reviews_repository.get_average_rating_for_book(book_id)

    async def delete_reviews_for_book(self, book_id: ObjectId):
        await self.__reviews_repository.delete_reviews_for_book(book_id)

    async def delete_reviews_for_books(self, book_ids: list[ObjectId]):
        await self.__reviews_repository.delete_reviews_for_books(book_ids)

    async def delete_reviews_by_user(self, user_id: ObjectId):
        await self.__reviews_repository.delete_reviews_by_user(user_id)

    async def delete(self, review_id: ObjectId):
        review = await self.__get_review_by_id_if_exists(review_id)
        await self.__reviews_repository.delete(review)

    async def __get_review_by_id_if_exists(self, review_id: ObjectId) -> Review:
        review = await self.__reviews_repository.get_one(review_id)
        if not review:
            raise ObjectNotFoundException(
                detail="Review with id " + str(review_id) + " not found"
            )
        return review
