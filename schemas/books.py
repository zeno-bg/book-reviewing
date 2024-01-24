from datetime import datetime
from enum import Enum
from typing import Optional

from odmantic import ObjectId
from pydantic import BaseModel, model_validator, Field


class BaseBookSchema(BaseModel):
    isbn: str = Field(min_length=10, max_length=13)
    title: str = Field(min_length=3, max_length=300)
    description: str = Field(min_length=10, max_length=1000)
    publication_date: datetime
    author_id: ObjectId


class BookPatchSchema(BaseModel):
    isbn: Optional[str] = Field(min_length=10, max_length=13, default=None)
    title: Optional[str] = Field(min_length=3, max_length=300, default=None)
    description: Optional[str] = Field(min_length=10, max_length=1000, default=None)
    publication_date: Optional[datetime] = None
    author_id: Optional[ObjectId] = None

    @model_validator(mode='after')
    def check_object_not_empty(self) -> 'BookPatchSchema':
        if self.isbn is None and self.title is None and self.description is None\
                and self.publication_date is None and self.author_id is None:
            raise ValueError('All fields cannot be empty')
        return self


class BookOutSchema(BaseBookSchema):
    id: Optional[ObjectId] = None
    average_rating: float


class BookFilterEnum(str, Enum):
    isbn = "isbn"
    title = "title"
    description = "description"
    publication_date = "publication_date"
    author_id = "author_id"
