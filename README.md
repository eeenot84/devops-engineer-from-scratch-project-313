### Hexlet tests and linter status:
[![Actions Status](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions)

[![CI Status](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions)

# Flask App

Flask URL shortener с CRUD API, PostgreSQL (SQLModel), Sentry и деплоем в Yandex Serverless Containers.

## Демо

https://bbas83kfi3oo3s9cv3na.containers.yandexcloud.net/

```bash
curl https://bbas83kfi3oo3s9cv3na.containers.yandexcloud.net/ping
```

## API (короткие ссылки)

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/links` | Список ссылок |
| `POST` | `/api/links` | Создать ссылку (`201`) |
| `GET` | `/api/links/<id>` | Получить ссылку |
| `PUT` | `/api/links/<id>` | Обновить ссылку |
| `DELETE` | `/api/links/<id>` | Удалить (`204`) |

Пример создания:

```bash
curl -X POST https://bbas83kfi3oo3s9cv3na.containers.yandexcloud.net/api/links \
  -H 'Content-Type: application/json' \
  -d '{"original_url":"https://example.com/long-url","short_name":"exmpl"}'
```

При конфликте `short_name` ответ: `409` и `{"error":"Entity with short_name already exists"}`.

## Локальный запуск

1. Скопируйте `.env.example` → `.env`.
2. Поднимите PostgreSQL и приложение:

```bash
make compose-up
```

Или только БД через compose и приложение локально:

```bash
docker compose up -d db
cp .env.example .env   # DATABASE_URL на localhost:5433
make run
```

Приложение: `http://localhost:8080`.

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `PORT` | Порт приложения (локально `8080`; в Serverless Containers задаёт платформа) |
| `DATABASE_URL` | PostgreSQL, например `postgresql://app:app@localhost:5432/appdb` |
| `BASE_URL` | Базовый URL для поля `short_url` (`{BASE_URL}/r/{short_name}`) |
| `SENTRY_DSN` | DSN Sentry (опционально) |

При старте приложения таблицы создаются автоматически (`SQLModel.metadata.create_all`).

## Docker

```bash
docker build -t flask-app .
docker run -p 8080:8080 \
  -e DATABASE_URL="postgresql://app:app@host.docker.internal:5432/appdb" \
  -e BASE_URL="http://localhost:8080" \
  flask-app
```

Или одной командой: `make compose-up`.

## Деплой: Yandex Cloud + SourceCraft

| Ресурс | Значение |
|--------|----------|
| Folder ID | `b1geg64v3vhkruo9j5ba` |
| Service Account | `github-action` (`ajedcqfhms8dprb7p0cg`) |
| Container Registry | `crpbebkq9vcs5fd300rv` |
| Container | `flask-app` |
| Service connection | `default-service-connection` |

Push в SourceCraft запускает сборку и деплой:

```bash
git push sourcecraft main
```

В `revision-env` задайте реальный `DATABASE_URL` Managed PostgreSQL и `BASE_URL` (URL контейнера).

## Тесты

```bash
make test-lint
```
