from odmantic import AIOEngine, ObjectId

from models import User


class UsersRepository:
    mongo_engine: AIOEngine

    def __init__(self, mongo_engine: AIOEngine):
        self.mongo_engine = mongo_engine

    async def save(self, user: User) -> User:
        return await self.mongo_engine.save(user)

    async def get_one(self, user_id: ObjectId) -> User | None:
        user: User = await self.mongo_engine.find_one(User, User.id == user_id)
        return user

    async def get_all(self) -> list[User]:
        return await self.mongo_engine.find(User)

    async def delete(self, user: User):
        await self.mongo_engine.delete(user)
