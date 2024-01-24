from odmantic import AIOEngine, ObjectId
from odmantic.query import QueryExpression

from books_reviewing.exceptions import database_exception_wrapper
from books_reviewing.models import Book


class BooksRepository:
    mongo_engine: AIOEngine

    def __init__(self, mongo_engine: AIOEngine):
        self.mongo_engine = mongo_engine

    @database_exception_wrapper
    async def save(self, book: Book) -> Book:
        return await self.mongo_engine.save(book)

    @database_exception_wrapper
    async def get_one(self, book_id: ObjectId) -> Book | None:
        book: Book = await self.mongo_engine.find_one(Book, Book.id == book_id)
        return book

    @database_exception_wrapper
    async def get_all(self) -> list[Book]:
        return await self.mongo_engine.find(Book)

    @database_exception_wrapper
    async def delete(self, book: Book):
        await self.mongo_engine.delete(book)

    @database_exception_wrapper
    async def query(
        self,
        sort: str,
        sort_direction: str,
        page: int,
        size: int,
        filters_dict: dict[str, str | ObjectId] = None,
        without_count: bool = False,
    ) -> (list[Book], int):
        queries = []
        if len(filters_dict) > 0:
            for filter_attribute_name in filters_dict.keys():
                queries.append(
                    QueryExpression(
                        eval("Book." + filter_attribute_name)
                        == filters_dict[filter_attribute_name]
                    )
                )

        items = await self.mongo_engine.find(
            Book,
            *queries,
            sort=eval("Book." + sort + "." + sort_direction + "()"),
            skip=(page - 1) * size,
            limit=size
        )

        if without_count:
            return items, None

        total_count = await self.mongo_engine.count(Book, *queries)

        return items, total_count

    @database_exception_wrapper
    async def count_books_for_author(self, author_id: ObjectId) -> int:
        return await self.mongo_engine.count(Book, Book.author_id == author_id)

    @database_exception_wrapper
    async def get_books_for_author(self, author_id: ObjectId) -> list[Book]:
        return await self.mongo_engine.find(Book, Book.author_id == author_id)

    @database_exception_wrapper
    async def delete_books_for_author(self, author_id: ObjectId):
        return await self.mongo_engine.remove(Book, Book.author_id == author_id)
