"""Integration tests for API routers.

Add your module-specific router tests here after creating modules.

Example test structure:
```python
from httpx import AsyncClient
from fastapi import status


class TestProductRouter:
    async def test_create_product(self, api_client: AsyncClient) -> None:
        response = await api_client.post(
            "/v1/products",
            json={"name": "Test Product"},
        )
        assert response.status_code == status.HTTP_201_CREATED
```
"""
