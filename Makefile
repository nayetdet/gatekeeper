.PHONY: install run migrate

install:
	uv sync --all-groups --all-packages

run: migrate
	uv run python -m gatekeeper

migrate:
	mkdir -p data
	uv run alembic upgrade head
