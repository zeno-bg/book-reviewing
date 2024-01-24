from enum import Enum
from typing import Optional

from odmantic import ObjectId
from pydantic import BaseModel, model_validator, Field


class BaseAuthorSchema(BaseModel):
    id: Optional[ObjectId] = None
    name: str = Field(min_length=3, max_length=200)
    bio: str


class AuthorOutSchema(BaseAuthorSchema):
    books_count: int


class AuthorPatchSchema(BaseModel):
    name: Optional[str] = Field(min_length=3, max_length=200, default=None)
    bio: Optional[str] = None

    @model_validator(mode='after')
    def check_object_not_empty(self) -> 'AuthorPatchSchema':
        if self.name is None and self.bio is None:
            raise ValueError('All fields cannot be empty')
        return self


class AuthorFilterEnum(str, Enum):
    name = "name"
    bio = "bio"
