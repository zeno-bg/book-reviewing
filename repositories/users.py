from typing import Any

from odmantic import AIOEngine, ObjectId
from odmantic.query import QueryExpression

from exceptions import DatabaseException, database_exception_wrapper
from models import User


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
    async def query(self, sort: str, sort_direction: str, filters_dict: dict[str, str] = None) -> list[User]:
        queries = []
        if len(filters_dict) > 0:
            for filter in filters_dict.keys():
                queries.append(QueryExpression(eval('User.' + filter) == filters_dict[filter]))

        return await self.mongo_engine.find(User, *queries, sort=eval('User.' + sort + '.' + sort_direction + '()'))
