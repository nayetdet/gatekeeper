# Build Stage
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder
ENV UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Runtime Stage
FROM python:3.13-slim-trixie
ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update  \
    && apt-get install -y --no-install-recommends \
        libasound2 \
        libgl1 \
        libglib2.0-0 \
        libgtk-3-0 \
        libx11-xcb1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app
RUN camoufox fetch

COPY docker/uv/scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

WORKDIR /app
VOLUME ["/app/data"]
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-m", "src.gatekeeper.main"]
