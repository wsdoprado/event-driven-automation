FROM python:3.12-slim AS base

# build stage
FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# copy files
WORKDIR /workspace
COPY --from=uv_files uv.lock /workspace/
COPY --from=uv_files pyproject.toml /workspace/
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --no-dev
COPY src/ /workspace
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev

# run stage
FROM base
COPY --from=builder /workspace /workspace
ENV PATH="/workspace/.venv/bin:$PATH"
WORKDIR /workspace
