all: fmt lint db test

ci: sync-all fmt lint upgrade-db db test

sync:
	uv sync

sync-all:
	uv sync --all-groups

fmt:
	uv run ruff format
	uv run ruff check --select I --fix

lint:
	uv run ruff check .
	uv run mypy .

upgrade-db:
	uv run alembic upgrade head

db:
	uv run alembic check

test:
	uv run pytest

test-build:
	docker build -t tmp .
	docker rmi tmp:latest
