from fastapi import status
from httpx import AsyncClient


async def test_health_endpoint(api_client: AsyncClient) -> None:
    """Test health check endpoint."""
    response = await api_client.get("/v1/health")
    response.raise_for_status()
    assert response.status_code == status.HTTP_200_OK
