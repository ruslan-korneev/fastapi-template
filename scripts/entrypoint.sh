#!/bin/bash

uv run alembic upgrade head

# execute command
exec "$@"
