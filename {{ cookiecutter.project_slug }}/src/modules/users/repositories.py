from uuid import UUID

from sqlalchemy import select

from src.core.types.repositories import BaseRepository
from src.modules.users.dto import UserCreateDTO, UserReadDTO, UserUpdateDTO
from src.modules.users.models import User


class UserRepository(BaseRepository[User, UserCreateDTO, UserReadDTO]):
    """Repository for User entity."""

    _model = User
    _create_dto = UserCreateDTO
    _read_dto = UserReadDTO

    async def get_by_id(self, user_id: UUID) -> UserReadDTO | None:
        """Get user by ID."""
        query = select(self._model).where(self._model.id == user_id)
        result = await self._session.execute(query)
        instance = result.scalar_one_or_none()

        if instance is None:
            return None

        return self._read_dto.model_validate(instance)

    async def get_by_email(self, email: str) -> UserReadDTO | None:
        """Get user by email."""
        query = select(self._model).where(self._model.email == email.lower())
        result = await self._session.execute(query)
        instance = result.scalar_one_or_none()

        if instance is None:
            return None

        return self._read_dto.model_validate(instance)

    async def update(self, user_id: UUID, data: UserUpdateDTO) -> UserReadDTO | None:
        """Update user by ID."""
        query = select(self._model).where(self._model.id == user_id)
        result = await self._session.execute(query)
        instance = result.scalar_one_or_none()

        if instance is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(instance, field, value)

        await self._session.flush()
        await self._session.refresh(instance)

        return self._read_dto.model_validate(instance)

    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID. Returns True if deleted, False if not found."""
        query = select(self._model).where(self._model.id == user_id)
        result = await self._session.execute(query)
        instance = result.scalar_one_or_none()

        if instance is None:
            return False

        await self._session.delete(instance)
        await self._session.flush()

        return True
