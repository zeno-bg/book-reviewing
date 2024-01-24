import datetime

from fastapi.exceptions import RequestValidationError
from odmantic import ObjectId

from exceptions import ObjectNotFoundException
from models import User
from repositories.users import UsersRepository
from schemas.base import SortEnum
from schemas.users import BaseUserSchema, UserPatchSchema, UserFilterEnum


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

    async def query(self, filter_attributes: list[UserFilterEnum] = None, filter_values: list[str] = None,
                    sort: UserFilterEnum = None, sort_direction: SortEnum = None,
                    page: int = None, size: int = None) -> (list[User], int):
        filters_dict = {}
        if filter_attributes and filter_values:
            if len(filter_attributes) != len(filter_values):
                raise RequestValidationError("Wrong number of filter attributes and values!")
            i = 0
            for attribute in filter_attributes:
                if attribute == UserFilterEnum.birthday:
                    filters_dict[attribute.lower()] = datetime.datetime.fromisoformat(filter_values[i])
                else:
                    filters_dict[attribute.lower()] = filter_values[i]
                i += 1
        return await self.__users_repository.query(filters_dict=filters_dict,
                                                   sort=sort if sort else UserFilterEnum.name,
                                                   sort_direction=sort_direction.lower() if sort_direction else 'asc',
                                                   page=page if page else 1, size=size if size else 10)

    async def delete(self, user_id: ObjectId):
        user = await self.__get_user_by_id_if_exists(user_id)
        await self.__users_repository.delete(user)

    async def __get_user_by_id_if_exists(self, user_id: ObjectId) -> User:
        user = await self.__users_repository.get_one(user_id)
        if not user:
            raise ObjectNotFoundException(detail='User with id ' + str(user_id) + ' not found')
        return user
