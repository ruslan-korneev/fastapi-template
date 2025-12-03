from uuid import uuid4

from src.modules.users.dto import UserCreateDTO, UserReadDTO, UserUpdateDTO
from src.modules.users.services import UserService


class TestUserService:
    """Unit tests for UserService."""

    async def test_create_user(self, user_service: UserService) -> None:
        """Test creating a user."""
        user = await user_service.create_user(
            UserCreateDTO(email="create@example.com", name="Create User"),
        )

        assert user.email == "create@example.com"
        assert user.name == "Create User"
        assert user.is_active is True

    async def test_get_user(
        self,
        user_service: UserService,
        sample_user: UserReadDTO,
    ) -> None:
        """Test getting a user by ID."""
        user = await user_service.get_user(sample_user.id)

        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email

    async def test_get_user_not_found(self, user_service: UserService) -> None:
        """Test getting a user that doesn't exist."""
        user = await user_service.get_user(uuid4())

        assert user is None

    async def test_get_user_by_email(
        self,
        user_service: UserService,
        sample_user: UserReadDTO,
    ) -> None:
        """Test getting a user by email."""
        user = await user_service.get_user_by_email(sample_user.email)

        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email

    async def test_get_user_by_email_case_insensitive(
        self,
        user_service: UserService,
        sample_user: UserReadDTO,
    ) -> None:
        """Test that email lookup is case-insensitive."""
        user = await user_service.get_user_by_email(sample_user.email.upper())

        assert user is not None
        assert user.id == sample_user.id

    async def test_get_user_by_email_not_found(
        self,
        user_service: UserService,
    ) -> None:
        """Test getting a user by email that doesn't exist."""
        user = await user_service.get_user_by_email("nonexistent@example.com")

        assert user is None

    async def test_get_all_users(
        self,
        user_service: UserService,
        sample_user: UserReadDTO,
        second_sample_user: UserReadDTO,
    ) -> None:
        """Test getting all users."""
        users = await user_service.get_all_users()

        assert len(users) == 2  # noqa: PLR2004
        assert sample_user in users
        assert second_sample_user in users

    async def test_update_user(
        self,
        user_service: UserService,
        sample_user: UserReadDTO,
    ) -> None:
        """Test updating a user."""
        updated = await user_service.update_user(
            sample_user.id,
            UserUpdateDTO(name="Updated Name"),
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.email == sample_user.email

    async def test_update_user_not_found(self, user_service: UserService) -> None:
        """Test updating a user that doesn't exist."""
        updated = await user_service.update_user(
            uuid4(),
            UserUpdateDTO(name="Updated Name"),
        )

        assert updated is None

    async def test_delete_user(
        self,
        user_service: UserService,
        sample_user: UserReadDTO,
    ) -> None:
        """Test deleting a user."""
        deleted = await user_service.delete_user(sample_user.id)

        assert deleted is True

        # Verify user is gone
        user = await user_service.get_user(sample_user.id)
        assert user is None

    async def test_delete_user_not_found(self, user_service: UserService) -> None:
        """Test deleting a user that doesn't exist."""
        deleted = await user_service.delete_user(uuid4())

        assert deleted is False
