.PHONY: run test lint test-lint

run:
	uv run python main.py

test:
	uv run pytest

lint:
	uv run ruff check .

test-lint:
	uv run pytest
	uv run ruff check .
