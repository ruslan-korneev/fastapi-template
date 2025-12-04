from uuid import uuid4

from src.modules.users.dto import UserCreateDTO, UserReadDTO, UserUpdateDTO
from src.modules.users.repositories import UserRepository


class TestUserRepository:
    """Unit tests for UserRepository."""

    async def test_save(self, user_repository: UserRepository) -> None:
        """Test saving a new user."""
        user = await user_repository.save(
            UserCreateDTO(email="repo@example.com", name="Repo User"),
        )

        assert user.email == "repo@example.com"
        assert user.name == "Repo User"
        assert user.is_active is True
        assert user.id is not None

    async def test_get_all(
        self,
        user_repository: UserRepository,
        sample_user: UserReadDTO,
        second_sample_user: UserReadDTO,
    ) -> None:
        """Test getting all users."""
        users = await user_repository.get_all()
        users_list = list(users)

        assert len(users_list) == 2  # noqa: PLR2004
        assert sample_user in users_list
        assert second_sample_user in users_list

    async def test_get_by_id(
        self,
        user_repository: UserRepository,
        sample_user: UserReadDTO,
    ) -> None:
        """Test getting a user by ID."""
        user = await user_repository.get_by_id(sample_user.id)

        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email

    async def test_get_by_id_not_found(self, user_repository: UserRepository) -> None:
        """Test getting a user by ID that doesn't exist."""
        user = await user_repository.get_by_id(uuid4())

        assert user is None

    async def test_get_by_email(
        self,
        user_repository: UserRepository,
        sample_user: UserReadDTO,
    ) -> None:
        """Test getting a user by email."""
        user = await user_repository.get_by_email(sample_user.email)

        assert user is not None
        assert user.id == sample_user.id

    async def test_get_by_email_case_insensitive(
        self,
        user_repository: UserRepository,
        sample_user: UserReadDTO,
    ) -> None:
        """Test that email lookup is case-insensitive."""
        user = await user_repository.get_by_email(sample_user.email.upper())

        assert user is not None
        assert user.id == sample_user.id

    async def test_get_by_email_not_found(self, user_repository: UserRepository) -> None:
        """Test getting a user by email that doesn't exist."""
        user = await user_repository.get_by_email("nonexistent@example.com")

        assert user is None

    async def test_update(
        self,
        user_repository: UserRepository,
        sample_user: UserReadDTO,
    ) -> None:
        """Test updating a user."""
        updated = await user_repository.update(
            sample_user.id,
            UserUpdateDTO(name="Updated Repo Name"),
        )

        assert updated is not None
        assert updated.name == "Updated Repo Name"
        assert updated.email == sample_user.email

    async def test_update_not_found(self, user_repository: UserRepository) -> None:
        """Test updating a user that doesn't exist."""
        updated = await user_repository.update(
            uuid4(),
            UserUpdateDTO(name="Updated Name"),
        )

        assert updated is None

    async def test_delete(
        self,
        user_repository: UserRepository,
        sample_user: UserReadDTO,
    ) -> None:
        """Test deleting a user."""
        deleted = await user_repository.delete(sample_user.id)

        assert deleted is True

        # Verify user is gone
        user = await user_repository.get_by_id(sample_user.id)
        assert user is None

    async def test_delete_not_found(self, user_repository: UserRepository) -> None:
        """Test deleting a user that doesn't exist."""
        deleted = await user_repository.delete(uuid4())

        assert deleted is False
