### Hexlet tests and linter status:
[![Actions Status](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions)

[![CI Status](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions)

# Flask App

Короткий URL-сервис: Flask + PostgreSQL + UI. Деплой в Yandex Serverless Containers.

**Демо:** https://bbas83kfi3oo3s9cv3na.containers.yandexcloud.net/

## Локально

```bash
make install
docker compose up -d db
cp .env.example .env
make run
```

- API: http://localhost:8080  
- UI: http://localhost:5173  

Всё в одном контейнере (Nginx + UI + API):

```bash
make compose-up
```

→ http://localhost:8080

## API

| Метод | Путь |
|-------|------|
| `GET` / `POST` | `/api/links` |
| `GET` / `PUT` / `DELETE` | `/api/links/<id>` |
| `GET` | `/r/<short_name>` — редирект |
| `GET` | `/ping` |

Список с пагинацией: `?range=[0,10]` (заголовок `Content-Range`).

## Env

| Переменная | Зачем |
|------------|--------|
| `PORT` | Порт (локально `8080`, в Yandex — `8080`) |
| `DATABASE_URL` | PostgreSQL |
| `BASE_URL` | База для `short_url` |
| `CORS_ORIGINS` | CORS (по умолчанию localhost:5173) |
| `SENTRY_DSN` | Sentry (опционально) |

## Деплой

```bash
git push sourcecraft main
```

В SourceCraft нужен секрет `DATABASE_URL` и в окружении контейнера — `BASE_URL`.

## Тесты

```bash
make test-lint
```
