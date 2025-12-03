"""File update functions for project setup."""

import re
from pathlib import Path

from setup_project.config import ProjectConfig

PROJECT_ROOT = Path(__file__).parent.parent


def update_pyproject(config: ProjectConfig) -> None:
    """Update pyproject.toml with project configuration."""
    filepath = PROJECT_ROOT / "pyproject.toml"
    content = filepath.read_text()

    # Update project name
    content = re.sub(
        r'^name = ".*"',
        f'name = "{config.name}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )

    # Update description
    content = re.sub(
        r'^description = ".*"',
        f'description = "{config.description}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )

    # Update author
    content = re.sub(
        r'\{ name = ".*", email = ".*" \}',
        f'{{ name = "{config.author_name}", email = "{config.author_email}" }}',
        content,
        count=1,
    )

    filepath.write_text(content)


def update_env_file(config: ProjectConfig, filepath: Path) -> None:
    """Update a single .env file with database configuration."""
    content = filepath.read_text()

    # Update project title/description
    content = re.sub(
        r"^PROJECT_TITLE=.*$",
        f"PROJECT_TITLE={config.name}",
        content,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r"^PROJECT_DESCRIPTION=.*$",
        f"PROJECT_DESCRIPTION={config.description}",
        content,
        flags=re.MULTILINE,
    )

    # Update database configuration
    content = re.sub(
        r"^DB__HOST=.*$",
        f"DB__HOST={config.db_host}",
        content,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r"^DB__PORT=.*$",
        f"DB__PORT={config.db_port}",
        content,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r"^DB__USERNAME=.*$",
        f"DB__USERNAME={config.db_user}",
        content,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r"^DB__PASSWORD=.*$",
        f"DB__PASSWORD={config.db_password}",
        content,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r"^DB__NAME=.*$",
        f"DB__NAME={config.db_name}",
        content,
        flags=re.MULTILINE,
    )

    filepath.write_text(content)


def update_env_files(config: ProjectConfig) -> None:
    """Update both .env and .env.example files."""
    env_file = PROJECT_ROOT / ".env"
    env_example = PROJECT_ROOT / ".env.example"

    if env_file.exists():
        update_env_file(config, env_file)

    if env_example.exists():
        update_env_file(config, env_example)


def update_readme(config: ProjectConfig) -> None:
    """Update README.md with project information."""
    filepath = PROJECT_ROOT / "README.md"
    content = filepath.read_text()

    # Update title
    content = re.sub(
        r"^# FastAPI Template",
        f"# {config.name}",
        content,
        count=1,
        flags=re.MULTILINE,
    )

    # Update GitHub URLs and badges if github_repo is provided
    if config.github_repo:
        # Normalize repo URL (remove https:// prefix if present)
        repo = config.github_repo
        if repo.startswith("https://"):
            repo = repo[8:]
        if repo.startswith("github.com/"):
            repo = repo[11:]

        # Update CI badge
        content = re.sub(
            r"\[!\[CI\]\(https://github\.com/[^/]+/[^/]+/actions/workflows/ci\.yml/badge\.svg\)\]"
            r"\(https://github\.com/[^/]+/[^/]+/actions/workflows/ci\.yml\)",
            f"[![CI](https://github.com/{repo}/actions/workflows/ci.yml/badge.svg)]"
            f"(https://github.com/{repo}/actions/workflows/ci.yml)",
            content,
        )

        # Update codecov badge (remove token)
        content = re.sub(
            r"\[!\[codecov\]\(https://codecov\.io/gh/[^/]+/[^/]+/graph/badge\.svg\?token=[^)]+\)\]"
            r"\(https://codecov\.io/gh/[^/]+/[^)]+\)",
            f"[![codecov](https://codecov.io/gh/{repo}/graph/badge.svg)]" f"(https://codecov.io/gh/{repo})",
            content,
        )

    # Update clone directory in Quick Start
    content = re.sub(
        r"^cd fastapi-template$",
        f"cd {config.name}",
        content,
        flags=re.MULTILINE,
    )

    # Update docker build command
    content = re.sub(
        r"docker build -t fastapi-template \.",
        f"docker build -t {config.name} .",
        content,
    )
    content = re.sub(
        r"docker run -p 8000:8000 --env-file \.env fastapi-template",
        f"docker run -p 8000:8000 --env-file .env {config.name}",
        content,
    )

    filepath.write_text(content)


def cleanup_ci_files(config: ProjectConfig) -> None:
    """Remove unused CI configuration files."""
    github_dir = PROJECT_ROOT / ".github"
    gitlab_file = PROJECT_ROOT / ".gitlab-ci.yml"

    if config.ci_platform == "github":
        # Keep GitHub Actions, remove GitLab CI
        if gitlab_file.exists():
            gitlab_file.unlink()
    elif config.ci_platform == "gitlab":
        # Keep GitLab CI, remove GitHub Actions
        if github_dir.exists():
            import shutil

            shutil.rmtree(github_dir)
    else:  # none
        # Remove both
        if gitlab_file.exists():
            gitlab_file.unlink()
        if github_dir.exists():
            import shutil

            shutil.rmtree(github_dir)


def apply_all_updates(config: ProjectConfig) -> list[str]:
    """Apply all updates and return list of updated files."""
    updated: list[str] = []

    update_pyproject(config)
    updated.append("pyproject.toml")

    update_env_files(config)
    if (PROJECT_ROOT / ".env").exists():
        updated.append(".env")
    if (PROJECT_ROOT / ".env.example").exists():
        updated.append(".env.example")

    update_readme(config)
    updated.append("README.md")

    cleanup_ci_files(config)
    if config.ci_platform == "github":
        updated.append("Removed .gitlab-ci.yml")
    elif config.ci_platform == "gitlab":
        updated.append("Removed .github/")
    elif config.ci_platform == "none":
        updated.append("Removed .gitlab-ci.yml")
        updated.append("Removed .github/")

    return updated
