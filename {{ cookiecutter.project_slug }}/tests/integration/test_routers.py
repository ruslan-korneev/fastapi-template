from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from src.modules.users.dto import UserReadDTO


class TestUserRouter:
    """Integration tests for user CRUD endpoints."""

    async def test_create_user(self, api_client: AsyncClient) -> None:
        """Test creating a new user."""
        response = await api_client.post(
            "/v1/users",
            json={"email": "new@example.com", "name": "New User"},
        )
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["name"] == "New User"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    async def test_create_user_duplicate_email(
        self,
        api_client: AsyncClient,
        sample_user: UserReadDTO,
    ) -> None:
        """Test that creating a user with duplicate email fails."""
        response = await api_client.post(
            "/v1/users",
            json={"email": sample_user.email, "name": "Another User"},
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_create_user_integrity_error(self, api_client: AsyncClient) -> None:
        """Test that non-unique IntegrityError returns 500."""
        with patch(
            "src.modules.users.services.UserService.create_user",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.side_effect = IntegrityError("stmt", "params", Exception("other error"))
            response = await api_client.post(
                "/v1/users",
                json={"email": "test@example.com", "name": "Test User"},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "internal_error"

    async def test_create_user_invalid_email(self, api_client: AsyncClient) -> None:
        """Test that creating a user with invalid email fails validation."""
        response = await api_client.post(
            "/v1/users",
            json={"email": "not-an-email", "name": "Test User"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_user_missing_fields(self, api_client: AsyncClient) -> None:
        """Test that creating a user with missing required fields fails validation."""
        response = await api_client.post(
            "/v1/users",
            json={"name": "Test User"},  # Missing email
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = await api_client.post(
            "/v1/users",
            json={"email": "test@example.com"},  # Missing name
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_users(
        self,
        api_client: AsyncClient,
        sample_user: UserReadDTO,
        second_sample_user: UserReadDTO,
    ) -> None:
        """Test getting paginated users."""
        expected_users_list = [sample_user, second_sample_user]

        response = await api_client.get("/v1/users")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "has_more" in data

        # Verify items
        items = [UserReadDTO.model_validate(user) for user in data["items"]]
        assert len(items) == len(expected_users_list)
        assert items == expected_users_list
        assert data["total"] == 2  # noqa: PLR2004
        assert data["has_more"] is False

    async def test_get_user_by_id(
        self,
        api_client: AsyncClient,
        sample_user: UserReadDTO,
    ) -> None:
        """Test getting a user by ID."""
        response = await api_client.get(f"/v1/users/{sample_user.id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == str(sample_user.id)
        assert data["email"] == sample_user.email

    async def test_get_user_not_found(self, api_client: AsyncClient) -> None:
        """Test getting a non-existent user."""
        response = await api_client.get(f"/v1/users/{uuid4()}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_user(
        self,
        api_client: AsyncClient,
        sample_user: UserReadDTO,
    ) -> None:
        """Test updating a user."""
        response = await api_client.patch(
            f"/v1/users/{sample_user.id}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == sample_user.email

    async def test_update_user_not_found(self, api_client: AsyncClient) -> None:
        """Test updating a non-existent user."""
        response = await api_client.patch(
            f"/v1/users/{uuid4()}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_user(
        self,
        api_client: AsyncClient,
        sample_user: UserReadDTO,
    ) -> None:
        """Test deleting a user."""
        response = await api_client.delete(f"/v1/users/{sample_user.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = await api_client.get(f"/v1/users/{sample_user.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_user_not_found(self, api_client: AsyncClient) -> None:
        """Test deleting a non-existent user."""
        response = await api_client.delete(f"/v1/users/{uuid4()}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
