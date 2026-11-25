import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.contact import ContactStatus


def _strip(value: object) -> object:
    if isinstance(value, str):
        return value.strip()
    return value


class ContactRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=5000)

    @field_validator("name", "subject", "message", mode="before")
    @classmethod
    def strip_required(cls, value: object) -> object:
        return _strip(value)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("phone", mode="before")
    @classmethod
    def blank_phone_to_none(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value


class ContactCreated(BaseModel):
    id: uuid.UUID
    status: ContactStatus
