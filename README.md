### Hexlet tests and linter status:
[![Actions Status](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions)

[![CI Status](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions)

# Flask App

Простое Flask-приложение с эндпоинтом `/ping` и мониторингом ошибок через Sentry.

## Демо

Приложение развёрнуто на Render (HTTPS):

https://devops-engineer-from-scratch-project-313.onrender.com

Проверка:

```bash
curl https://devops-engineer-from-scratch-project-313.onrender.com/ping
```

Ожидаемый ответ: `pong`.

## Локальный запуск

1. Убедитесь, что установлен `uv`.
2. В корне проекта выполните:

```bash
make run
```

Приложение будет доступно на `http://localhost:8080/ping`.

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `PORT` | Порт приложения (по умолчанию `8080`) |
| `DATABASE_URL` | URL подключения к базе данных |
| `SENTRY_DSN` | DSN проекта в Sentry для отправки ошибок |

## Docker

Сборка образа:

```bash
docker build -t flask-app .
```

Запуск контейнера:

```bash
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e DATABASE_URL="postgresql://user:password@host:5432/dbname" \
  -e SENTRY_DSN="https://<key>@sentry.io/<project>" \
  flask-app
```

## Деплой на Render

1. Создайте Web Service на [Render](https://render.com/).
2. Подключите репозиторий GitHub.
3. Выберите **Language — Docker**.
4. Укажите **Instance Type — Free**.
5. В **Environment Variables** добавьте:
   - `PORT=8080`
   - `DATABASE_URL` — URL вашей PostgreSQL (можно создать Free PostgreSQL на Render)
   - `SENTRY_DSN` — DSN из [Sentry](https://sentry.io/)
6. После деплоя приложение будет доступно по HTTPS.

## Sentry

Для проверки отправки ошибок откройте:

```text
/error
```

Ошибка должна появиться в проекте Sentry.

## Тесты и линтер

Локально:

```bash
make test
make lint
```

Или одной командой:

```bash
make test-lint
```

В CI (GitHub Actions) на каждый push и pull request в `main` автоматически запускаются `pytest` и `ruff`.
