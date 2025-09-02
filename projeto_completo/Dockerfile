FROM python:3.12-slim AS base

# build stage
FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# copy files
WORKDIR /app

COPY --from=uv_files uv.lock /app/
COPY --from=uv_files pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --no-dev
COPY src/ /app/src
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev

# run stage
FROM base
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app

ENV PYTHONPATH=/app/src

RUN mkdir -p /var/log/proxyarpnd