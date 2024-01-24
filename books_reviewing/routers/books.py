from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Params
from fastapi_pagination.links import Page
from odmantic import ObjectId

from books_reviewing.dependencies import get_books_service
from books_reviewing.models import Book
from books_reviewing.schemas.base import SortEnum
from books_reviewing.schemas.books import (
    BookPatchSchema,
    BaseBookSchema,
    BookFilterEnum,
    BookOutSchema,
)
from books_reviewing.services.books import BooksService

router = APIRouter()

BooksServiceDep = Annotated[BooksService, Depends(get_books_service)]


@router.post("/")
async def create(book: BaseBookSchema, books_service: BooksServiceDep) -> Book:
    return await books_service.create(book)


@router.patch("/{book_id}")
async def update(
    book_id: ObjectId, book_new: BookPatchSchema, books_service: BooksServiceDep
) -> Book:
    return await books_service.update(book_id, book_new)


@router.get("/{book_id}")
async def get_one(book_id: ObjectId, books_service: BooksServiceDep) -> BookOutSchema:
    return await books_service.get_one(book_id)


@router.get("/")
async def query(
    books_service: BooksServiceDep,
    filter_attributes: Annotated[list[BookFilterEnum], Query()] = None,
    filter_values: Annotated[list[str], Query()] = None,
    sort: BookFilterEnum = None,
    sort_direction: SortEnum = None,
    page: int = None,
    size: int = None,
) -> Page[Book]:
    items, total_count = await books_service.query(
        filter_attributes, filter_values, sort, sort_direction, page, size
    )
    params = Params().model_construct(page=page, size=size)
    return Page.create(items=items, params=params, total=total_count)


@router.delete("/{book_id}", status_code=204)
async def delete(book_id: ObjectId, books_service: BooksServiceDep):
    await books_service.delete(book_id)
