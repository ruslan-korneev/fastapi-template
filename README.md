# FastAPI Template

[![CI](https://github.com/ruslan-korneev/fastapi-template/actions/workflows/ci.yml/badge.svg)](https://github.com/ruslan-korneev/fastapi-template/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ruslan-korneev/fastapi-template/branch/main/graph/badge.svg)](https://codecov.io/gh/ruslan-korneev/fastapi-template)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![mypy](https://img.shields.io/badge/mypy-strict-blue.svg)](http://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready FastAPI template with SQLAlchemy, dependency injection, Sentry integration, and comprehensive testing setup.

## Features

- **FastAPI** with async support
- **SQLAlchemy 2.0** with async sessions and PostgreSQL
- **Alembic** for database migrations
- **Pydantic v2** for data validation
- **Dependency Injector** for IoC/DI container
- **Sentry** for error tracking
- **Loguru** for structured logging with request ID tracking
- **Comprehensive testing** with pytest, coverage requirements
- **Code quality** with ruff, mypy (strict mode)

### Production-Ready Features

- **API Versioning** - URL prefix versioning (`/v1/...`)
- **Rate Limiting** - In-memory token bucket algorithm with configurable limits
- **Request ID Tracking** - UUID per request, logged and returned in headers
- **Global Exception Handling** - Consistent error response format
- **Configurable CORS** - Environment-based CORS configuration
- **Pagination** - Offset-based pagination with metadata

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- PostgreSQL 17+

## Quick Start

### 1. Setup Environment

```bash
git clone <repository-url>
cd fastapi-template

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv sync --all-groups
```

### 2. Configure Database

```bash
cp .env.example .env
# Edit .env with your database credentials
```

Run database migrations:

```bash
uv run alembic upgrade head
```

### 3. Start API Server

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Access API documentation at http://localhost:8000/docs

## API Endpoints

All endpoints are prefixed with `/v1/`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/health` | Health check with DB connectivity |
| GET | `/v1/users` | List users (paginated) |
| POST | `/v1/users` | Create user |
| GET | `/v1/users/{id}` | Get user by ID |
| PATCH | `/v1/users/{id}` | Update user |
| DELETE | `/v1/users/{id}` | Delete user |

### Pagination

List endpoints return paginated responses:

```json
{
  "items": [...],
  "total": 100,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```

Query parameters: `?limit=20&offset=0`

### Response Headers

All responses include:
- `X-Request-ID` - Unique request identifier
- `X-RateLimit-Limit` - Rate limit ceiling
- `X-RateLimit-Remaining` - Remaining requests

### Error Response Format

```json
{
  "error": "NotFoundError",
  "detail": "Resource not found",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Development

### Code Quality

```bash
make fmt      # Format code with ruff
make lint     # Run linting with ruff and mypy
make test     # Run test suite with pytest
make db       # Validate database migrations
make          # Run all checks (fmt, lint, db, test)
```

### Project Structure

```
src/
├── core/                  # Application core
│   ├── api/               # Router aggregation with versioning
│   ├── dependencies/      # DI setup (containers, db, http)
│   ├── exceptions.py      # Custom exception classes
│   ├── middleware/        # Request ID, Rate limiting
│   └── types/             # Base types (DTO, Repository, Pagination)
├── db/                    # Database configuration
│   ├── base.py            # SQLAlchemy base model
│   └── session.py         # Async session factory
├── modules/               # Feature modules
│   └── users/             # Example CRUD module
│       ├── models.py      # SQLAlchemy model
│       ├── dto.py         # Pydantic DTOs
│       ├── repositories.py # Data access layer
│       ├── services.py    # Business logic
│       └── routers.py     # API endpoints
└── config.py              # Application settings

tests/
├── conftest.py            # Common fixtures
├── mimic/                 # Test doubles (stubs, fakes, mocks)
├── benchmark/             # Performance tests
├── integration/           # API endpoint and database tests
└── unit/                  # Unit tests
    └── modules/
        └── users/         # User module tests
```

## Architecture Patterns

### Repository Pattern

Base repository (`src/core/types/repositories.py`) provides generic CRUD operations:

```python
class UserRepository(BaseRepository[User, UserCreateDTO, UserReadDTO]):
    _model = User
    _create_dto = UserCreateDTO
    _read_dto = UserReadDTO

    # Inherited methods: get_all(), get_paginated(), save(), save_bulk()
```

### Service Layer

Business logic is separated from data access:

```python
class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repository = UserRepository(session)

    async def get_users_paginated(
        self, limit: int = 20, offset: int = 0
    ) -> PaginatedResponse[UserReadDTO]:
        result = await self._repository.get_paginated(limit=limit, offset=offset)
        return PaginatedResponse.create(
            items=list(result.items),
            total=result.total,
            limit=limit,
            offset=offset,
        )
```

### Custom Exceptions

Use custom exceptions for consistent error handling:

```python
from src.core.exceptions import NotFoundError, ConflictError

# In service layer
if user is None:
    raise NotFoundError("User not found")

# Automatically returns:
# {"error": "NotFoundError", "detail": "User not found", "request_id": "..."}
```

### Dependency Injection

Using `dependency-injector` for managing application dependencies:

```python
class Container(DeclarativeContainer):
    wiring_config = WiringConfiguration(packages=["src"])
    db_session_maker = providers.Factory(AsyncSessionMaker)
```

## Adding a New Module

1. Create module directory: `src/modules/<name>/`

2. Add model in `models.py`:
```python
class MyModel(SAModel):
    __tablename__ = "my_models"
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    # ... fields
```

3. Define DTOs in `dto.py`:
```python
class MyModelCreateDTO(BaseDTO):
    # input fields

class MyModelReadDTO(BaseDTO):
    # output fields
```

4. Create repository in `repositories.py`:
```python
class MyModelRepository(BaseRepository[MyModel, MyModelCreateDTO, MyModelReadDTO]):
    _model = MyModel
    _create_dto = MyModelCreateDTO
    _read_dto = MyModelReadDTO
```

5. Add service layer in `services.py`

6. Define routes in `routers.py`

7. Register router in `src/core/api/routers.py`:
```python
from src.modules.my_module import router as my_router
v1_router.include_router(my_router)  # Note: register on v1_router
```

8. Create migration:
```bash
uv run alembic revision --autogenerate -m "add_my_model_table"
```

9. Add tests:
   - Unit tests in `tests/unit/modules/<name>/`
   - Integration tests in `tests/integration/`

## Configuration

Environment variables are loaded from `.env` file. See `.env.example` for available options.

### Key Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `DB__HOST` | PostgreSQL host | localhost |
| `DB__PORT` | PostgreSQL port | 5432 |
| `DB__NAME` | Database name | postgres |
| `DB__USERNAME` | Database user | postgres |
| `DB__PASSWORD` | Database password | postgres |
| `SENTRY__DSN` | Sentry DSN (optional) | - |
| `LOGGING_LEVEL` | Log level | INFO |
| `CORS__ALLOW_ORIGINS` | Allowed CORS origins | ["*"] |
| `CORS__ALLOW_CREDENTIALS` | Allow credentials | true |
| `CORS__MAX_AGE` | Preflight cache time | 600 |
| `RATE_LIMIT__ENABLED` | Enable rate limiting | true |
| `RATE_LIMIT__REQUESTS_PER_MINUTE` | Rate limit | 60 |
| `RATE_LIMIT__BURST_SIZE` | Burst allowance | 10 |

## Testing

Tests use transaction rollback for isolation - each test runs in its own transaction that gets rolled back.

```bash
# Run all tests
make test

# Run by category
uv run pytest -k unit -v           # Unit tests only
uv run pytest -k integration -v    # Integration tests only
uv run pytest -k "not benchmark"   # Exclude benchmarks

# Run specific test file
uv run pytest tests/unit/modules/users/test_services.py -v

# Run tests matching pattern
uv run pytest -k "test_create" -v

# Run with coverage report
uv run pytest --cov-report=html
```

Coverage requirements: 80% line, 70% branch.

## Docker

Build and run with Docker:

```bash
docker build -t fastapi-template .
docker run -p 8000:8000 --env-file .env fastapi-template
```

## License

MIT
