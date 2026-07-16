# --- frontend static ---
FROM node:22-bookworm-slim AS frontend

WORKDIR /frontend
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts \
  && mkdir -p /public \
  && cp -r ./node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. /public/

# --- app + nginx ---
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update \
  && apt-get install -y --no-install-recommends nginx gettext-base \
  && rm -rf /var/lib/apt/lists/* \
  && rm -f /etc/nginx/sites-enabled/default

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY main.py database.py models.py ./
COPY nginx.conf.template docker-entrypoint.sh ./
COPY --from=frontend /public /app/public

RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 80 8080

CMD ["/app/docker-entrypoint.sh"]
