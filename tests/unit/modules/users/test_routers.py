"""Unit tests for user router handlers called directly (not via ASGI)."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from asyncpg import UniqueViolationError
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.core.types.dto import PaginatedResponse
from src.modules.users.dto import UserCreateDTO, UserReadDTO, UserUpdateDTO
from src.modules.users.routers import create_user, delete_user, get_user, get_users, update_user
from tests.mimic.session import FakeSessionMaker


@pytest.fixture
def mock_user_service() -> AsyncMock:
    """Mock UserService for unit tests."""
    return AsyncMock()


@pytest.fixture
def mock_user() -> UserReadDTO:
    """Create a mock user DTO."""
    return UserReadDTO(
        id=uuid4(),
        email="mock@example.com",
        name="Mock User",
        is_active=True,
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
    )


class TestUserRouterHandlers:
    """Unit tests for router handlers."""

    async def test_create_user_success(
        self,
        mock_user_service: AsyncMock,
        mock_user: UserReadDTO,
    ) -> None:
        """Test create_user handler success path."""
        mock_user_service.create_user = AsyncMock(return_value=mock_user)

        session_mock = AsyncMock()
        session_maker = FakeSessionMaker(session_mock)

        with patch("src.modules.users.routers.UserService", return_value=mock_user_service):
            result = await create_user(
                data=UserCreateDTO(email="test@example.com", name="Test User"),
                db_session_maker=session_maker,  # type: ignore[arg-type]
            )

        assert result == mock_user
        session_mock.commit.assert_called_once()

    async def test_create_user_unique_violation(self, mock_user_service: AsyncMock) -> None:
        """Test create_user handler with UniqueViolationError."""
        unique_error = UniqueViolationError("duplicate key")
        integrity_error = IntegrityError("stmt", "params", unique_error)
        integrity_error.orig = MagicMock()
        integrity_error.orig.__cause__ = unique_error

        mock_user_service.create_user = AsyncMock(side_effect=integrity_error)

        session_mock = AsyncMock()
        session_maker = FakeSessionMaker(session_mock)

        with (
            patch("src.modules.users.routers.UserService", return_value=mock_user_service),
            pytest.raises(HTTPException) as exc_info,
        ):
            await create_user(
                data=UserCreateDTO(email="test@example.com", name="Test User"),
                db_session_maker=session_maker,  # type: ignore[arg-type]
            )

        assert exc_info.value.status_code == 409  # noqa: PLR2004
        session_mock.rollback.assert_called_once()

    async def test_create_user_other_integrity_error(self, mock_user_service: AsyncMock) -> None:
        """Test create_user handler with non-unique IntegrityError."""
        integrity_error = IntegrityError("stmt", "params", Exception("other error"))
        integrity_error.orig = None

        mock_user_service.create_user = AsyncMock(side_effect=integrity_error)

        session_mock = AsyncMock()
        session_maker = FakeSessionMaker(session_mock)

        with (
            patch("src.modules.users.routers.UserService", return_value=mock_user_service),
            pytest.raises(HTTPException) as exc_info,
        ):
            await create_user(
                data=UserCreateDTO(email="test@example.com", name="Test User"),
                db_session_maker=session_maker,  # type: ignore[arg-type]
            )

        assert exc_info.value.status_code == 500  # noqa: PLR2004
        session_mock.rollback.assert_called_once()

    async def test_get_users_success(
        self,
        mock_user_service: AsyncMock,
        mock_user: UserReadDTO,
    ) -> None:
        """Test get_users handler with pagination."""
        paginated_response = PaginatedResponse[UserReadDTO](
            items=[mock_user],
            total=1,
            limit=20,
            offset=0,
            has_more=False,
        )
        mock_user_service.get_users_paginated = AsyncMock(return_value=paginated_response)

        session_mock = AsyncMock()
        session_maker = FakeSessionMaker(session_mock)

        with patch("src.modules.users.routers.UserService", return_value=mock_user_service):
            result = await get_users(
                db_session_maker=session_maker,  # type: ignore[arg-type]
                limit=20,
                offset=0,
            )

        assert result == paginated_response
        assert result.items == [mock_user]
        assert result.total == 1

    async def test_get_user_success(
        self,
        mock_user_service: AsyncMock,
        mock_user: UserReadDTO,
    ) -> None:
        """Test get_user handler success path."""
        mock_user_service.get_user = AsyncMock(return_value=mock_user)

        session_mock = AsyncMock()
        session_maker = FakeSessionMaker(session_mock)

        with patch("src.modules.users.routers.UserService", return_value=mock_user_service):
            result = await get_user(
                user_id=mock_user.id,
                db_session_maker=session_maker,  # type: ignore[arg-type]
            )

        assert result == mock_user

    async def test_get_user_not_found(self, mock_user_service: AsyncMock) -> None:
        """Test get_user handler when user not found."""
        mock_user_service.get_user = AsyncMock(return_value=None)

        session_mock = AsyncMock()
        session_maker = FakeSessionMaker(session_mock)

        with (
            patch("src.modules.users.routers.UserService", return_value=mock_user_service),
            pytest.raises(HTTPException) as exc_info,
        ):
            await get_user(
                user_id=uuid4(),
                db_session_maker=session_maker,  # type: ignore[arg-type]
            )

        assert exc_info.value.status_code == 404  # noqa: PLR2004

    async def test_update_user_success(
        self,
        mock_user_service: AsyncMock,
        mock_user: UserReadDTO,
    ) -> None:
        """Test update_user handler success path."""
        updated_user = UserReadDTO(
            id=mock_user.id,
            email=mock_user.email,
            name="Updated Name",
            is_active=mock_user.is_active,
            created_at=mock_user.created_at,
            updated_at=datetime.now(tz=UTC),
        )
        mock_user_service.update_user = AsyncMock(return_value=updated_user)

        session_mock = AsyncMock()
        session_maker = FakeSessionMaker(session_mock)

        with patch("src.modules.users.routers.UserService", return_value=mock_user_service):
            result = await update_user(
                user_id=mock_user.id,
                data=UserUpdateDTO(name="Updated Name"),
                db_session_maker=session_maker,  # type: ignore[arg-type]
            )

        assert result == updated_user
        session_mock.commit.assert_called_once()

    async def test_update_user_not_found(self, mock_user_service: AsyncMock) -> None:
        """Test update_user handler when user not found."""
        mock_user_service.update_user = AsyncMock(return_value=None)

        session_mock = AsyncMock()
        session_maker = FakeSessionMaker(session_mock)

        with (
            patch("src.modules.users.routers.UserService", return_value=mock_user_service),
            pytest.raises(HTTPException) as exc_info,
        ):
            await update_user(
                user_id=uuid4(),
                data=UserUpdateDTO(name="Updated Name"),
                db_session_maker=session_maker,  # type: ignore[arg-type]
            )

        assert exc_info.value.status_code == 404  # noqa: PLR2004

    async def test_delete_user_success(
        self,
        mock_user_service: AsyncMock,
        mock_user: UserReadDTO,
    ) -> None:
        """Test delete_user handler success path."""
        mock_user_service.delete_user = AsyncMock(return_value=True)

        session_mock = AsyncMock()
        session_maker = FakeSessionMaker(session_mock)

        with patch("src.modules.users.routers.UserService", return_value=mock_user_service):
            await delete_user(
                user_id=mock_user.id,
                db_session_maker=session_maker,  # type: ignore[arg-type]
            )

        session_mock.commit.assert_called_once()

    async def test_delete_user_not_found(self, mock_user_service: AsyncMock) -> None:
        """Test delete_user handler when user not found."""
        mock_user_service.delete_user = AsyncMock(return_value=False)

        session_mock = AsyncMock()
        session_maker = FakeSessionMaker(session_mock)

        with (
            patch("src.modules.users.routers.UserService", return_value=mock_user_service),
            pytest.raises(HTTPException) as exc_info,
        ):
            await delete_user(
                user_id=uuid4(),
                db_session_maker=session_maker,  # type: ignore[arg-type]
            )

        assert exc_info.value.status_code == 404  # noqa: PLR2004
