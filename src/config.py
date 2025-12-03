import sys
from pathlib import Path
from typing import Literal

import loguru
from loguru import logger
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("settings",)


class DbSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = "postgres"
    username: str = "postgres"
    password: SecretStr = SecretStr("postgres")

    def get_url(
        self,
        scheme: Literal["postgres", "postgresql", "postgresql+asyncpg"] = "postgresql+asyncpg",
        db_name: str | None = None,
    ) -> SecretStr:
        pwd = self.password.get_secret_value()
        name = db_name or self.name
        return SecretStr(f"{scheme}://{self.username}:{pwd}@{self.host}:{self.port}/{name}")


class SentrySettings(BaseModel):
    dsn: SecretStr = SecretStr("")
    enable_tracing: bool = True
    traces_sample_rate: float = 1.0
    profiles_sample_rate: float = 1.0


class CORSSettings(BaseModel):
    allow_origins: list[str] = ["*"]
    allow_origin_regex: str | None = r"^https?://.*$"
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
    expose_headers: list[str] = []
    max_age: int = 600


class RateLimitSettings(BaseModel):
    enabled: bool = True
    requests_per_minute: int = 60
    burst_size: int = 10


class Config(BaseSettings):
    root_dir: Path = Path(__file__).parent.parent.resolve()
    logging_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    environment: str = "development"

    project_title: str = "FastAPI Template"
    project_description: str = "Production-ready FastAPI template"

    db: DbSettings = DbSettings()
    sentry: SentrySettings = SentrySettings()
    cors: CORSSettings = CORSSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()

    model_config = SettingsConfigDict(
        env_file=f"{root_dir}/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
        env_nested_delimiter="__",
        extra="ignore",  # ignores extra keys from env file
    )


settings = Config()

# Logging Configuration
logger.remove(0)


def _format_log_record(record: "loguru.Record") -> str:
    """Format log record with optional request_id."""
    base = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " "<red>[{level}]</red> | "
    # Include request_id if present in extra context
    if record["extra"].get("request_id"):
        base += "<yellow>[{extra[request_id]}]</yellow> | "
    base += "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>: " "<green>{message}</green>\n"
    return base


logger.add(
    sys.stderr,
    format=_format_log_record,
    colorize=True,
    level=settings.logging_level,
    backtrace=True,
    diagnose=True,
)
