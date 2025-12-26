# Build Stage
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Runtime Stage
FROM python:3.13-slim-trixie
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
RUN useradd -m app
COPY --from=builder --chown=app:app /app /app
COPY --chown=app:app docker/uv/scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER app
VOLUME ["/app/config", "/app/data", "/app/tmp"]
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-m", "src.gatekeeper.main"]
