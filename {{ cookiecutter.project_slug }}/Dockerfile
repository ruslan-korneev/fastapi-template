FROM python:3.14.3-slim-trixie

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential=12.12 \
      libffi-dev=3.4.8-2 \
 && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.10.12 /uv /uvx /bin/

COPY . /app
WORKDIR /app

RUN uv sync --frozen

ENTRYPOINT ["scripts/entrypoint.sh"]
