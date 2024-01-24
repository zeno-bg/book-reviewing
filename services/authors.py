import datetime

from fastapi.exceptions import RequestValidationError
from odmantic import ObjectId

from exceptions import ObjectNotFoundException
from models import Author
from repositories.authors import AuthorsRepository
from schemas.base import SortEnum
from schemas.authors import BaseAuthorSchema, AuthorPatchSchema, AuthorFilterEnum


class AuthorsService:
    __authors_repository: AuthorsRepository

    def __init__(self, authors_repository: AuthorsRepository):
        self.__authors_repository = authors_repository

    async def create(self, author: BaseAuthorSchema) -> Author:
        author_in_db = Author(**author.model_dump())
        return await self.__authors_repository.save(author_in_db)

    async def update(self, author_id: ObjectId, author_new: AuthorPatchSchema) -> Author:
        author = await self.__get_author_by_id_if_exists(author_id)
        author.model_update(author_new, exclude_unset=True)
        await self.__authors_repository.save(author)
        return author

    async def get_one(self, author_id: ObjectId) -> Author:
        return await self.__get_author_by_id_if_exists(author_id)

    async def query(self, filter_attributes: list[AuthorFilterEnum] = None, filter_values: list[str] = None,
                    sort: AuthorFilterEnum = None, sort_direction: SortEnum = None,
                    page: int = None, size: int = None) -> (list[Author], int):
        filters_dict = {}
        if filter_attributes and filter_values:
            if len(filter_attributes) != len(filter_values):
                raise RequestValidationError("Wrong number of filter attributes and values!")

            filters_dict = dict(zip(filter_attributes, filter_values))

        return await self.__authors_repository.query(filters_dict=filters_dict,
                                                   sort=sort if sort else AuthorFilterEnum.name,
                                                   sort_direction=sort_direction.lower() if sort_direction else 'asc',
                                                   page=page if page else 1, size=size if size else 10)

    async def delete(self, author_id: ObjectId):
        author = await self.__get_author_by_id_if_exists(author_id)
        await self.__authors_repository.delete(author)

    async def __get_author_by_id_if_exists(self, author_id: ObjectId) -> Author:
        author = await self.__authors_repository.get_one(author_id)
        if not author:
            raise ObjectNotFoundException(detail='Author with id ' + str(author_id) + ' not found')
        return author
