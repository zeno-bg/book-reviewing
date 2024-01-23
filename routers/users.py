from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from odmantic import ObjectId

from dependencies import get_users_service
from exceptions import ObjectNotFoundException
from models import User
from schemas.users import UserPatchSchema, BaseUserSchema
from services.users import UsersService

router = APIRouter()

UsersServiceDep = Annotated[UsersService, Depends(get_users_service)]


@router.post('/')
async def create(user: BaseUserSchema, users_service: UsersServiceDep) -> User:
    return await users_service.create(user)


@router.patch('/{user_id}')
async def update(user_id: ObjectId, user_new: UserPatchSchema, users_service: UsersServiceDep) -> User:
    try:
        return await users_service.update(user_id, user_new)
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.detail)


@router.get('/{user_id}')
async def get_one(user_id: ObjectId, users_service: UsersServiceDep) -> User:
    try:
        return await users_service.get_one(user_id)
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.detail)


@router.get('/')
async def get(users_service: UsersServiceDep) -> list[User]:
    return await users_service.get_all()


@router.delete('/{user_id}', status_code=204)
async def delete(user_id: ObjectId, users_service: UsersServiceDep):
    try:
        await users_service.delete(user_id)
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.detail)
