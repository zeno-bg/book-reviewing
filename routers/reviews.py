from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Params
from fastapi_pagination.links import Page
from odmantic import ObjectId

from dependencies import get_reviews_service
from models import Review
from schemas.base import SortEnum
from schemas.reviews import ReviewPatchSchema, BaseReviewSchema, ReviewFilterEnum
from services.reviews import ReviewsService

router = APIRouter()

ReviewsServiceDep = Annotated[ReviewsService, Depends(get_reviews_service)]


@router.post("/")
async def create(
    review: BaseReviewSchema, reviews_service: ReviewsServiceDep
) -> Review:
    return await reviews_service.create(review)


@router.patch("/{review_id}")
async def update(
    review_id: ObjectId,
    review_new: ReviewPatchSchema,
    reviews_service: ReviewsServiceDep,
) -> Review:
    return await reviews_service.update(review_id, review_new)


@router.get("/{review_id}")
async def get_one(review_id: ObjectId, reviews_service: ReviewsServiceDep) -> Review:
    return await reviews_service.get_one(review_id)


@router.get("/")
async def query(
    reviews_service: ReviewsServiceDep,
    filter_attributes: Annotated[list[ReviewFilterEnum], Query()] = None,
    filter_values: Annotated[list[str], Query()] = None,
    sort: ReviewFilterEnum = None,
    sort_direction: SortEnum = None,
    page: int = None,
    size: int = None,
) -> Page[Review]:
    items, total_count = await reviews_service.query(
        filter_attributes, filter_values, sort, sort_direction, page, size
    )
    params = Params().model_construct(page=page, size=size)
    return Page.create(items=items, params=params, total=total_count)


@router.delete("/{review_id}", status_code=204)
async def delete(review_id: ObjectId, reviews_service: ReviewsServiceDep):
    await reviews_service.delete(review_id)
