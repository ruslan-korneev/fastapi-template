"""Project configuration dataclass."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class ProjectConfig:
    """Configuration collected from user prompts."""

    name: str  # kebab-case project name
    package_name: str  # snake_case (derived from name)
    description: str
    author_name: str
    author_email: str
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    ci_platform: Literal["github", "gitlab", "none"]
    github_repo: str | None = None

    @classmethod
    def derive_package_name(cls, name: str) -> str:
        """Convert kebab-case name to snake_case package name."""
        return name.replace("-", "_")

    @classmethod
    def derive_db_name(cls, name: str) -> str:
        """Convert kebab-case name to snake_case database name."""
        return name.replace("-", "_")
