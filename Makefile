.PHONY: install run migrations

install:
	uv sync --all-groups --all-packages

run: migrations
	uv run python -m src.gatekeeper.main

migrations:
	mkdir -p data
	uv run alembic upgrade head
