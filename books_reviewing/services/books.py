import asyncio
import datetime
from typing import TYPE_CHECKING

from fastapi.exceptions import RequestValidationError
from odmantic import ObjectId

from books_reviewing.exceptions import ObjectNotFoundException
from books_reviewing.models import Book
from books_reviewing.repositories.books import BooksRepository
from books_reviewing.schemas.base import SortEnum
from books_reviewing.schemas.books import (
    BaseBookSchema,
    BookPatchSchema,
    BookFilterEnum,
    BookOutSchema,
)
from books_reviewing.services.authors import AuthorsService

if TYPE_CHECKING:
    from books_reviewing.services.reviews import ReviewsService


class BooksService:
    reviews_service: "ReviewsService"

    __books_repository: BooksRepository
    __authors_service: AuthorsService

    def __init__(
        self,
        books_repository: BooksRepository,
        authors_service: AuthorsService,
        reviews_service: "ReviewsService" = None,
    ):
        self.__books_repository = books_repository
        self.__authors_service = authors_service
        self.reviews_service = reviews_service

    async def create(self, book: BaseBookSchema) -> Book:
        await self.__authors_service.get_one(book.author_id)
        book_in_db = Book(**book.model_dump())
        return await self.__books_repository.save(book_in_db)

    async def update(self, book_id: ObjectId, book_new: BookPatchSchema) -> Book:
        book = await self.__get_book_by_id_if_exists(book_id)
        if book_new.author_id:
            await self.__authors_service.get_one(book.author_id)
        book.model_update(book_new, exclude_unset=True)
        await self.__books_repository.save(book)
        return book

    async def get_one(self, book_id: ObjectId) -> BookOutSchema:
        book, average_rating = await asyncio.gather(
            self.__get_book_by_id_if_exists(book_id),
            self.reviews_service.get_average_rating_for_book(book_id),
        )
        return BookOutSchema(**book.model_dump(), average_rating=average_rating)

    async def get_one_without_rating(self, book_id: ObjectId) -> BookOutSchema:
        book = await self.__get_book_by_id_if_exists(book_id)
        return BookOutSchema(**book.model_dump(), average_rating=0)

    async def query(
        self,
        filter_attributes: list[BookFilterEnum] = None,
        filter_values: list[str] = None,
        sort: BookFilterEnum = None,
        sort_direction: SortEnum = None,
        page: int = None,
        size: int = None,
    ) -> (list[Book], int):
        filters_dict = {}
        if filter_attributes and filter_values:
            if len(filter_attributes) != len(filter_values):
                raise RequestValidationError(
                    "Wrong number of filter attributes and values!"
                )
            i = 0
            for attribute in filter_attributes:
                if attribute == BookFilterEnum.publication_date:
                    filters_dict[attribute.lower()] = datetime.datetime.fromisoformat(
                        filter_values[i]
                    )
                elif attribute == BookFilterEnum.author_id:
                    filters_dict[attribute.lower()] = ObjectId(filter_values[i])
                else:
                    filters_dict[attribute.lower()] = filter_values[i]
                i += 1
        return await self.__books_repository.query(
            filters_dict=filters_dict,
            sort=sort if sort else BookFilterEnum.title,
            sort_direction=sort_direction.lower() if sort_direction else "asc",
            page=page if page else 1,
            size=size if size else 10,
        )

    async def get_book_count_for_author(self, author_id: ObjectId) -> int:
        return await self.__books_repository.count_books_for_author(author_id)

    async def delete_books_for_author(self, author_id: ObjectId):
        books = await self.__books_repository.get_books_for_author(author_id)
        book_ids = [book.id for book in books]
        await asyncio.gather(
            self.__books_repository.delete_books_for_author(author_id),
            self.reviews_service.delete_reviews_for_books(book_ids),
        )

    async def delete(self, book_id: ObjectId):
        book = await self.__get_book_by_id_if_exists(book_id)
        await asyncio.gather(
            self.__books_repository.delete(book),
            self.reviews_service.delete_reviews_for_book(book_id),
        )

    async def __get_book_by_id_if_exists(self, book_id: ObjectId) -> Book:
        book = await self.__books_repository.get_one(book_id)
        if not book:
            raise ObjectNotFoundException(
                detail="Book with id " + str(book_id) + " not found"
            )
        return book
