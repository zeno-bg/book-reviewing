from enum import Enum
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from odmantic import ObjectId

from dependencies import get_users_service
from exceptions import ObjectNotFoundException
from models import User
from schemas.base import SortEnum
from schemas.users import UserPatchSchema, BaseUserSchema, UserFilterEnum
from services.users import UsersService

router = APIRouter()

UsersServiceDep = Annotated[UsersService, Depends(get_users_service)]


@router.post('/')
async def create(user: BaseUserSchema, users_service: UsersServiceDep) -> User:
    return await users_service.create(user)


@router.patch('/{user_id}')
async def update(user_id: ObjectId, user_new: UserPatchSchema, users_service: UsersServiceDep) -> User:
    return await users_service.update(user_id, user_new)


@router.get('/{user_id}')
async def get_one(user_id: ObjectId, users_service: UsersServiceDep) -> User:
    return await users_service.get_one(user_id)


@router.get('/')
async def query(users_service: UsersServiceDep, filter_attributes: Annotated[list[UserFilterEnum], Query()] = None,
                filter_values: Annotated[list[str], Query()] = None,
                sort: UserFilterEnum = None,
                sort_direction: SortEnum = None,
                ) -> list[User]:
    resp = await users_service.query(filter_attributes, filter_values, sort, sort_direction)
    return resp


@router.delete('/{user_id}', status_code=204)
async def delete(user_id: ObjectId, users_service: UsersServiceDep):
    await users_service.delete(user_id)
