from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T", bound="BaseDTO")


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    limit: int
    offset: int
    has_more: bool

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        limit: int,
        offset: int,
    ) -> "PaginatedResponse[T]":
        """Create a paginated response with has_more calculation."""
        return cls(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            has_more=offset + len(items) < total,
        )
