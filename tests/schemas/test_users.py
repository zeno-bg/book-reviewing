from datetime import datetime

import pytest

from schemas.users import (
    BaseUserSchema,
    UserPatchSchema,
    validate_email,
    validate_phone,
)

valid_emails = ["bill.clinton@usa.gov", "john@doe.com", "elon@x.com"]
invalid_emails = ["bill@clinton@usa", "alksdfjaklsdf", "@@@@@@", "@", "elon@elon"]

valid_phones = ["+359893428172", "0872233212", "+35938432342"]
invalid_phones = ["ajlskdfjasldf", "127389123123123", "12322"]


@pytest.mark.parametrize("email_to_validate", valid_emails)
def test_validate_email_email(email_to_validate: str):
    assert validate_email(email_to_validate) == email_to_validate


@pytest.mark.parametrize("email_to_validate", invalid_emails)
def test_invalid_email(email_to_validate: str):
    with pytest.raises(ValueError):
        validate_email(email_to_validate)


@pytest.mark.parametrize("phone_to_validate", valid_phones)
def test_valid_phone(phone_to_validate: str):
    assert validate_phone(phone_to_validate) == phone_to_validate


@pytest.mark.parametrize("phone_to_validate", invalid_phones)
def test_invalid_phone(phone_to_validate: str):
    with pytest.raises(ValueError):
        validate_phone(phone_to_validate)


def test_base_user_schema():
    data = {
        "name": "Nasko the Mint",
        "birthday": datetime(1990, 10, 12),
        "email": "nasko@mint.com",
        "phone": "+359872232124",
    }
    user = BaseUserSchema(**data)
    assert user.model_dump() == data


def test_empty_user_patch_schema():
    with pytest.raises(ValueError):
        UserPatchSchema()


@pytest.mark.parametrize("email_to_validate", invalid_emails)
def test_invalid_email_in_user_schemas(email_to_validate):
    data = {"email": email_to_validate}

    with pytest.raises(ValueError):
        BaseUserSchema(**data)

    with pytest.raises(ValueError):
        UserPatchSchema(**data)


@pytest.mark.parametrize("phone_to_validate", invalid_phones)
def test_invalid_phone_in_user_schemas(phone_to_validate):
    data = {"phone": phone_to_validate}

    with pytest.raises(ValueError):
        BaseUserSchema(**data)

    with pytest.raises(ValueError):
        UserPatchSchema(**data)
