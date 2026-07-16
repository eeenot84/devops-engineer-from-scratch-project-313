.PHONY: run test lint test-lint docker-build docker-run compose-up compose-down

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
	docker run --rm -p 8080:8080 \
		-e PORT=8080 \
		-e DATABASE_URL \
		-e BASE_URL \
		-e SENTRY_DSN \
		flask-app

compose-up:
	docker compose up --build -d

compose-down:
	docker compose down -v
