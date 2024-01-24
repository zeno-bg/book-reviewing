from odmantic import AIOEngine, ObjectId
from odmantic.query import QueryExpression

from books_reviewing.exceptions import database_exception_wrapper
from books_reviewing.models import User


class UsersRepository:
    mongo_engine: AIOEngine

    def __init__(self, mongo_engine: AIOEngine):
        self.mongo_engine = mongo_engine

    @database_exception_wrapper
    async def save(self, user: User) -> User:
        return await self.mongo_engine.save(user)

    @database_exception_wrapper
    async def get_one(self, user_id: ObjectId) -> User | None:
        user: User = await self.mongo_engine.find_one(User, User.id == user_id)
        return user

    @database_exception_wrapper
    async def get_all(self) -> list[User]:
        return await self.mongo_engine.find(User)

    @database_exception_wrapper
    async def delete(self, user: User):
        await self.mongo_engine.delete(user)

    @database_exception_wrapper
    async def query(
        self,
        sort: str,
        sort_direction: str,
        page: int,
        size: int,
        filters_dict: dict[str, str] = None,
    ) -> (list[User], int):
        queries = []
        if len(filters_dict) > 0:
            for filter_attribute_name in filters_dict.keys():
                queries.append(
                    QueryExpression(
                        eval("User." + filter_attribute_name)
                        == filters_dict[filter_attribute_name]
                    )
                )

        items = await self.mongo_engine.find(
            User,
            *queries,
            sort=eval("User." + sort + "." + sort_direction + "()"),
            skip=(page - 1) * size,
            limit=size
        )
        total_count = await self.mongo_engine.count(User, *queries)

        return items, total_count
