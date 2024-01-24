import datetime

from fastapi.exceptions import RequestValidationError
from odmantic import ObjectId

from exceptions import ObjectNotFoundException
from models import Book
from repositories.books import BooksRepository
from schemas.base import SortEnum
from schemas.books import BaseBookSchema, BookPatchSchema, BookFilterEnum
from services.authors import AuthorsService


class BooksService:
    __books_repository: BooksRepository
    __authors_service: AuthorsService

    def __init__(self, books_repository: BooksRepository, authors_service: AuthorsService):
        self.__books_repository = books_repository
        self.__authors_service = authors_service

    async def create(self, book: BaseBookSchema) -> Book:
        author = await self.__authors_service.get_one(book.author_id)
        book_in_db = Book(**book.model_dump(), author=author)
        return await self.__books_repository.save(book_in_db)

    async def update(self, book_id: ObjectId, book_new: BookPatchSchema) -> Book:
        book = await self.__get_book_by_id_if_exists(book_id)
        book.model_update(book_new, exclude_unset=True)
        await self.__books_repository.save(book)
        return book

    async def get_one(self, book_id: ObjectId) -> Book:
        return await self.__get_book_by_id_if_exists(book_id)

    async def query(self, filter_attributes: list[BookFilterEnum] = None, filter_values: list[str] = None,
                    sort: BookFilterEnum = None, sort_direction: SortEnum = None,
                    page: int = None, size: int = None) -> (list[Book], int):
        filters_dict = {}
        if filter_attributes and filter_values:
            if len(filter_attributes) != len(filter_values):
                raise RequestValidationError("Wrong number of filter attributes and values!")
            i = 0
            for attribute in filter_attributes:
                if attribute == BookFilterEnum.publication_date:
                    filters_dict[attribute.lower()] = datetime.datetime.fromisoformat(filter_values[i])
                elif attribute == BookFilterEnum.author_id:
                    filters_dict[attribute.lower()] = ObjectId(filter_values[i])
                else:
                    filters_dict[attribute.lower()] = filter_values[i]
                i += 1
        return await self.__books_repository.query(filters_dict=filters_dict,
                                                   sort=sort if sort else BookFilterEnum.title,
                                                   sort_direction=sort_direction.lower() if sort_direction else 'asc',
                                                   page=page if page else 1, size=size if size else 10)

    async def get_book_count_for_author(self, author_id: ObjectId) -> int:
        return await self.__books_repository.count_books_for_author(author_id)

    async def delete_books_for_author(self, author_id: ObjectId):
        return await self.__books_repository.delete_books_for_author(author_id)

    async def delete(self, book_id: ObjectId):
        book = await self.__get_book_by_id_if_exists(book_id)
        await self.__books_repository.delete(book)

    async def __get_book_by_id_if_exists(self, book_id: ObjectId) -> Book:
        book = await self.__books_repository.get_one(book_id)
        if not book:
            raise ObjectNotFoundException(detail='Book with id ' + str(book_id) + ' not found')
        return book
