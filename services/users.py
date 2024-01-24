from odmantic import ObjectId

from exceptions import ObjectNotFoundException
from models import User
from repositories.users import UsersRepository
from schemas.users import BaseUserSchema, UserPatchSchema


class UsersService:
    __users_repository: UsersRepository

    def __init__(self, users_repository: UsersRepository):
        self.__users_repository = users_repository

    async def create(self, user: BaseUserSchema) -> User:
        user_in_db = User(**user.model_dump())
        return await self.__users_repository.save(user_in_db)

    async def update(self, user_id: ObjectId, user_new: UserPatchSchema) -> User:
        user = await self.__get_user_by_id_if_exists(user_id)
        user.model_update(user_new, exclude_unset=True)
        await self.__users_repository.save(user)
        return user

    async def get_one(self, user_id: ObjectId) -> User:
        return await self.__get_user_by_id_if_exists(user_id)

    async def get_all(self) -> list[User]:
        return await self.__users_repository.get_all()

    async def delete(self, user_id: ObjectId):
        user = await self.__get_user_by_id_if_exists(user_id)
        await self.__users_repository.delete(user)

    async def __get_user_by_id_if_exists(self, user_id: ObjectId) -> User:
        user = await self.__users_repository.get_one(user_id)
        if not user:
            raise ObjectNotFoundException(detail='User with id ' + str(user_id) + ' not found')
        return user
