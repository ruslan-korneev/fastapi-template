import asyncio
from logging.config import fileConfig
from importlib import import_module
from pathlib import Path

from alembic import context
from loguru import logger
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio.engine import AsyncEngine, async_engine_from_config

from src.config import settings
from src.db.base import SAModel


def import_models(path: Path = Path("src/modules"), models_module_name: str = "models") -> None:
    """Recursively import all models from the modules directory.

    Discovers and imports models from:
    - Single files: module/models.py
    - Packages: module/models/__init__.py
    - Nested modules: module/submodule/models.py
    """
    # Walk through all directories under the base path recursively
    for current_dir in path.rglob("*"):
        if not current_dir.is_dir():
            continue

        if current_dir.name == "__pycache__":
            continue

        # Skip if this IS the models directory itself (avoid importing models.models)
        if current_dir.name == models_module_name:
            continue

        # Check if this directory has models.py or models/__init__.py
        has_models_file = (current_dir / f"{models_module_name}.py").exists()
        has_models_package = (current_dir / models_module_name / "__init__.py").exists()

        if not has_models_file and not has_models_package:
            continue

        # Convert path to module name
        # e.g., src/modules/domain/protocols -> src.modules.domain.protocols.models
        try:
            relative_path = current_dir.relative_to(path)
            base_module = str(path).replace("/", ".")
            if str(relative_path) == ".":
                # models.py is directly in path directory
                module = f"{base_module}.{models_module_name}"
            else:
                module = f"{base_module}.{str(relative_path).replace('/', '.')}.{models_module_name}"
        except ValueError:
            logger.debug(f"Skipping {current_dir} (outside base path)")
            continue

        try:
            import_module(module)
            logger.debug(f"Imported {module}")
        except ModuleNotFoundError as e:
            logger.exception(e)
            continue


import_models()

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

DB_URL = settings.db.get_url().get_secret_value()
config.set_main_option("sqlalchemy.url", DB_URL)

target_metadata = SAModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations(engine: AsyncEngine) -> None:
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    connection = context.config.attributes.get("connection", None)
    if not connection:
        configuration: dict[str, str] = config.get_section(  # type: ignore[assignment]
            config.config_ini_section,
        )
        configuration["sqlalchemy.url"] = DB_URL
        connection = async_engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )

        asyncio.run(run_async_migrations(connection))
    else:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
