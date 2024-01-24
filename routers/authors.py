from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Params
from fastapi_pagination.links import Page
from odmantic import ObjectId

from dependencies import get_authors_service
from models import Author
from schemas.base import SortEnum
from schemas.authors import AuthorPatchSchema, BaseAuthorSchema, AuthorFilterEnum, AuthorOutSchema
from services.authors import AuthorsService

router = APIRouter()

AuthorsServiceDep = Annotated[AuthorsService, Depends(get_authors_service)]


@router.post('/')
async def create(author: BaseAuthorSchema, authors_service: AuthorsServiceDep) -> Author:
    return await authors_service.create(author)


@router.patch('/{author_id}')
async def update(author_id: ObjectId, author_new: AuthorPatchSchema, authors_service: AuthorsServiceDep) -> Author:
    return await authors_service.update(author_id, author_new)


@router.get('/{author_id}')
async def get_one(author_id: ObjectId, authors_service: AuthorsServiceDep) -> AuthorOutSchema:
    return await authors_service.get_one(author_id)


@router.get('/')
async def query(authors_service: AuthorsServiceDep,
                filter_attributes: Annotated[list[AuthorFilterEnum], Query()] = None,
                filter_values: Annotated[list[str], Query()] = None,
                sort: AuthorFilterEnum = None,
                sort_direction: SortEnum = None,
                page: int = None,
                size: int = None,
                ) -> Page[Author]:
    items, total_count = await authors_service.query(filter_attributes, filter_values, sort, sort_direction, page, size)
    params = Params().model_construct(page=page, size=size)
    return Page.create(items=items, params=params, total=total_count)


@router.delete('/{author_id}', status_code=204, description="Also deletes all books for this author!")
async def delete(author_id: ObjectId, authors_service: AuthorsServiceDep):
    await authors_service.delete(author_id)
