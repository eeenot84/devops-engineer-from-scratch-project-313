.PHONY: setup install run run-backend run-frontend test lint test-lint docker-build docker-run compose-up compose-down

FRAMEWORK ?= flask

setup: install

install:
	uv sync
	npm install

run-backend:
ifeq ($(FRAMEWORK),flask)
	uv run python main.py
else
	$(error Unsupported FRAMEWORK=$(FRAMEWORK). Use FRAMEWORK=flask)
endif

run-frontend:
	npx start-hexlet-devops-deploy-crud-frontend

run:
	npx concurrently -n backend,frontend -c blue,magenta \
		"$(MAKE) run-backend FRAMEWORK=$(FRAMEWORK)" \
		"$(MAKE) run-frontend"

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
	docker run --rm -p 8080:80 \
		-e PORT=80 \
		-e DATABASE_URL \
		-e BASE_URL \
		-e SENTRY_DSN \
		-e CORS_ORIGINS \
		flask-app

compose-up:
	docker compose up --build -d

compose-down:
	docker compose down -v
