import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator, field_validator, Field


class BaseUserSchema(BaseModel):
    name: str = Field(min_length=3, max_length=200)
    birthday: datetime
    email: str
    phone: str

    # https://github.com/art049/odmantic/issues/397 - when this issue is resolved,
    # we will be able to return to regular Field validations

    @field_validator("email")
    @classmethod
    def email_must_match_regex(cls, value: str) -> str:
        return validate_email(value)

    @field_validator("phone")
    @classmethod
    def phone_must_match_regex(cls, value: str) -> str:
        return validate_phone(value)


class UserPatchSchema(BaseModel):
    name: Optional[str] = Field(min_length=3, max_length=200, default=None)
    birthday: Optional[datetime] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    @model_validator(mode='after')
    def check_object_not_empty(self) -> 'UserPatchSchema':
        if self.name is None and self.birthday is None and self.email is None and self.phone is None:
            raise ValueError('All fields cannot be empty')
        return self

    @field_validator("email")
    @classmethod
    def email_must_match_regex(cls, value: str) -> str:
        return validate_email(value)

    @field_validator("phone")
    @classmethod
    def phone_must_match_regex(cls, value: str) -> str:
        return validate_phone(value)


def validate_email(value: str) -> str:
    if not re.compile(r'[^@]+@[^@]+\.[^@]+').match(value):
        raise ValueError("Email is not valid")
    return value


def validate_phone(value: str) -> str:
    if not re.compile(r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$').match(value):
        raise ValueError("Phone is not valid")
    return value
