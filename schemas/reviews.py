from datetime import datetime
from enum import Enum
from typing import Optional

from odmantic import ObjectId
from pydantic import BaseModel, model_validator, Field


class BaseReviewSchema(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=2, max_length=1000)
    book_id: ObjectId
    user_id: ObjectId


class ReviewPatchSchema(BaseModel):
    rating: Optional[int] = Field(ge=1, le=5, default=None)
    comment: Optional[str] = Field(min_length=2, max_length=1000, default=None)
    book_id: Optional[ObjectId] = None
    user_id: Optional[ObjectId] = None

    @model_validator(mode='after')
    def check_object_not_empty(self) -> 'ReviewPatchSchema':
        if self.rating is None and self.comment is None and self.book_id is None and self.user_id is None:
            raise ValueError('All fields cannot be empty')
        return self


class ReviewFilterEnum(str, Enum):
    rating = "rating"
    comment = "comment"
    book_id = "book_id"
    user_id = "user_id"
