from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.types.dto import PaginatedResponse
from src.modules.users.dto import UserCreateDTO, UserReadDTO, UserUpdateDTO
from src.modules.users.repositories import UserRepository


class UserService:
    """Service layer for user operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._repository = UserRepository(session)

    async def create_user(self, data: UserCreateDTO) -> UserReadDTO:
        """Create a new user."""
        return await self._repository.save(data)

    async def get_user(self, user_id: UUID) -> UserReadDTO | None:
        """Get user by ID."""
        return await self._repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> UserReadDTO | None:
        """Get user by email."""
        return await self._repository.get_by_email(email)

    async def get_all_users(self) -> list[UserReadDTO]:
        """Get all users (unpaginated)."""
        users = await self._repository.get_all()
        return list(users)

    async def get_users_paginated(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedResponse[UserReadDTO]:
        """Get paginated users with metadata."""
        result = await self._repository.get_paginated(limit=limit, offset=offset)
        return PaginatedResponse.create(
            items=list(result.items),
            total=result.total,
            limit=limit,
            offset=offset,
        )

    async def update_user(self, user_id: UUID, data: UserUpdateDTO) -> UserReadDTO | None:
        """Update user by ID."""
        return await self._repository.update(user_id, data)

    async def delete_user(self, user_id: UUID) -> bool:
        """Delete user by ID."""
        return await self._repository.delete(user_id)
