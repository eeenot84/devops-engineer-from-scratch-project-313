.PHONY: run test lint test-lint docker-build docker-run

run:
	uv run python main.py

test:
	uv run pytest

lint:
	uv run ruff check .

test-lint:
	uv run pytest
	uv run ruff check .

docker-build:
	docker build -t flask-app .

docker-run:
	docker run --rm -p 8080:8080 -e PORT=8080 flask-app
