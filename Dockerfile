FROM python:3.13.6-slim-bullseye

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential=12.9 \
      libffi-dev=3.3-6 \
 && rm -rf /var/lib/apt/lists/*


COPY --from=ghcr.io/astral-sh/uv:0.9.2 /uv /uvx /bin/

COPY . /app
WORKDIR /app

RUN uv sync --frozen

ENTRYPOINT ["scripts/entrypoint.sh"]
