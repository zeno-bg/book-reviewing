from odmantic import AIOEngine, ObjectId
from odmantic.query import QueryExpression

from exceptions import database_exception_wrapper
from models import Author


class AuthorsRepository:
    mongo_engine: AIOEngine

    def __init__(self, mongo_engine: AIOEngine):
        self.mongo_engine = mongo_engine

    @database_exception_wrapper
    async def save(self, author: Author) -> Author:
        return await self.mongo_engine.save(author)

    @database_exception_wrapper
    async def get_one(self, author_id: ObjectId) -> Author | None:
        author: Author = await self.mongo_engine.find_one(Author, Author.id == author_id)
        return author

    @database_exception_wrapper
    async def get_all(self) -> list[Author]:
        return await self.mongo_engine.find(Author)

    @database_exception_wrapper
    async def delete(self, author: Author):
        await self.mongo_engine.delete(author)

    @database_exception_wrapper
    async def query(self, sort: str, sort_direction: str, page: int, size: int,
                    filters_dict: dict[str, str] = None) -> (list[Author], int):
        queries = []
        if len(filters_dict) > 0:
            for filter_attribute_name in filters_dict.keys():
                queries.append(QueryExpression(eval('Author.' + filter_attribute_name) == filters_dict[filter_attribute_name]))

        items = await self.mongo_engine.find(Author, *queries, sort=eval('Author.' + sort + '.' + sort_direction + '()'),
                                             skip=(page - 1) * size, limit=size)
        total_count = await self.mongo_engine.count(Author, *queries)

        return items, total_count
