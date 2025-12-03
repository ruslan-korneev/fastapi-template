from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from src.core.types.dto import BaseDTO


class UserCreateDTO(BaseDTO):
    """DTO for creating a new user."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserUpdateDTO(BaseDTO):
    """DTO for updating a user."""

    email: EmailStr | None = None
    name: str | None = Field(None, min_length=1, max_length=100)
    is_active: bool | None = None


class UserReadDTO(BaseDTO):
    """DTO for reading user data."""

    id: UUID
    email: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
