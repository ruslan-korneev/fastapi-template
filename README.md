# FastAPI Cookiecutter Template

A production-ready FastAPI project template with SQLAlchemy, dependency injection, Sentry integration, and comprehensive testing setup.

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
- **Rate Limiting** - In-memory token bucket algorithm
- **Request ID Tracking** - UUID per request in logs and headers
- **Global Exception Handling** - Consistent error response format
- **Configurable CORS** - Environment-based configuration
- **Pagination** - Offset-based pagination with metadata

## Requirements

- Python 3.10+
- [cookiecutter](https://cookiecutter.readthedocs.io/)
- [uv](https://docs.astral.sh/uv/) package manager

## Quick Start

### Install Cookiecutter

```bash
# Using pip
pip install cookiecutter

# Or using uv
uv tool install cookiecutter
```

### Generate Project

```bash
# From local directory
cookiecutter /path/to/fastapi-template

# From GitHub (after publishing)
cookiecutter gh:username/fastapi-template
```

### Interactive Prompts

You'll be prompted for the following options:

| Option | Description | Default |
|--------|-------------|---------|
| `project_name` | Project name (kebab-case) | `my-fastapi-project` |
| `project_description` | Short project description | `Production-ready FastAPI application` |
| `author_name` | Your full name | `Your Name` |
| `author_email` | Your email address | `you@example.com` |
| `github_username` | GitHub username (for badges) | *(empty)* |
| `python_version` | Python version | `3.13` |
| `ci_platform` | CI/CD platform | `github`, `gitlab`, or `none` |
| `license` | License type | `MIT`, `Apache-2.0`, `BSD-3-Clause`, or `None` |

### Example Session

```
$ cookiecutter fastapi-template

project_name [my-fastapi-project]: my-awesome-api
project_description [Production-ready FastAPI application]: My awesome API service
author_name [Your Name]: John Doe
author_email [you@example.com]: john@example.com
github_username []: johndoe
python_version [3.13]:
Select ci_platform:
1 - github
2 - gitlab
3 - none
Choose from 1, 2, 3 [1]: 1
Select license:
1 - MIT
2 - Apache-2.0
3 - BSD-3-Clause
4 - None
Choose from 1, 2, 3, 4 [1]: 1
```

### After Generation

The post-generation hook automatically:
- Initializes a git repository
- Installs dependencies with `uv sync`
- Copies `.env.example` to `.env`

Then you can:

```bash
cd my-awesome-api

# Edit .env with your database credentials
$EDITOR .env

# Run database migrations
uv run alembic upgrade head

# Run all quality checks
make

# Start the development server
uv run uvicorn main:app --reload
```

## Template Options Explained

### CI Platform

- **github**: Includes GitHub Actions workflow (`.github/workflows/ci.yml`)
- **gitlab**: Includes GitLab CI configuration (`.gitlab-ci.yml`)
- **none**: No CI configuration included

### License

- **MIT**: Permissive open-source license
- **Apache-2.0**: Permissive license with patent protection
- **BSD-3-Clause**: Permissive license with attribution
- **None**: No license file included

## Project Structure (Generated)

```
my-project/
├── .github/               # GitHub Actions (if selected)
├── .gitlab-ci.yml         # GitLab CI (if selected)
├── .env.example           # Environment template
├── pyproject.toml         # Project configuration
├── README.md              # Project documentation
├── Dockerfile             # Container configuration
├── Makefile               # Development commands
├── main.py                # Application entry point
├── alembic.ini            # Migration configuration
├── migrations/            # Database migrations
├── src/
│   ├── config.py          # Application settings
│   ├── core/              # Application core
│   │   ├── api/           # Router aggregation
│   │   ├── dependencies/  # DI setup
│   │   ├── middleware/    # Request ID, Rate limiting
│   │   └── types/         # Base types
│   ├── db/                # Database configuration
│   └── modules/           # Feature modules
│       └── users/         # Example CRUD module
└── tests/                 # Test suite
```

## Testing the Template

```bash
# Generate with defaults (no prompts)
cookiecutter . --no-input

# Generate with specific values
cookiecutter . --no-input \
  project_name="test-project" \
  ci_platform="gitlab" \
  license="Apache-2.0"

# Verify the generated project
cd test-project
make
```

## License

MIT
