# Build Stage
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS build
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
FROM python:3.14-slim-trixie
ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libasound2 \
        libgl1 \
        libglib2.0-0 \
        libgtk-3-0 \
        xauth \
        xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/.venv /app/.venv
RUN camoufox fetch

COPY --from=build /app/alembic /app/alembic
COPY --from=build /app/alembic.ini /app/alembic.ini
COPY --from=build /app/src /app/src
COPY --chmod=755 docker/scripts/entrypoint.sh /app/entrypoint.sh

WORKDIR /app
VOLUME ["/app/data"]
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-m", "gatekeeper"]
