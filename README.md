### Hexlet tests and linter status:
[![Actions Status](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions)

[![CI Status](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/eeenot84/devops-engineer-from-scratch-project-313/actions)

# Flask App

Простое Flask-приложение с эндпоинтом `/ping` и мониторингом ошибок через Sentry.
Деплой: **SourceCraft CI/CD → Yandex Container Registry → Serverless Containers**.

## Демо

После первого успешного деплоя URL контейнера появится в консоли Yandex Cloud → Serverless Containers → `flask-app` (поле «Ссылка для вызова»).

Проверка:

```bash
curl https://<CONTAINER_URL>/ping
```

Ожидаемый ответ: `pong`.

Подставьте фактический URL сюда после деплоя:

```text
https://<CONTAINER_ID>.containers.yandexcloud.net/ping
```

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

## Деплой: Yandex Cloud + SourceCraft

### Инфраструктура (уже создана в каталоге)

| Ресурс | Значение |
|--------|----------|
| Folder ID | `b1geg64v3vhkruo9j5ba` |
| Service Account | `github-action` (`ajedcqfhms8dprb7p0cg`) |
| Container Registry | `github-action` (`crpbebkq9vcs5fd300rv`) |
| Container name | `flask-app` |

Роли SA: `container-registry.images.pusher`, `serverless-containers.editor`, `iam.serviceAccounts.user`, `serverless-containers.admin`.

### Сервисное подключение в SourceCraft (один раз)

1. Откройте [SourceCraft](https://sourcecraft.dev/) → Организация → **Сервисные подключения**.
2. Создайте подключение с именем `default-service-connection`.
3. Укажите каталог `b1geg64v3vhkruo9j5ba` и SA `github-action`.
4. Область применения — этот репозиторий.

Нужна роль владельца организации SourceCraft.

### CI/CD

Конфигурация: [`.sourcecraft/ci.yaml`](.sourcecraft/ci.yaml).

При push в `main` в remote `sourcecraft`:

1. Получается IAM-токен через service connection.
2. Собирается Docker-образ (`linux/amd64`).
3. Образ пушится в `cr.yandex/crpbebkq9vcs5fd300rv/flask-app:latest`.
4. Деплоится публичная ревизия Serverless Container `flask-app` с env `PORT`, `DATABASE_URL`, `SENTRY_DSN`.

```bash
git push sourcecraft main
```

Статус: репозиторий → **CI/CD**.

## Sentry

1. Создайте проект Flask в [Sentry](https://sentry.io/).
2. Пропишите DSN в `revision-env` в `.sourcecraft/ci.yaml` (параметр `SENTRY_DSN`) и задеплойте снова.
3. Откройте `/error` — ошибка должна появиться в Sentry.

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

В GitHub Actions на каждый push и pull request в `main` автоматически запускаются `pytest` и `ruff`.
