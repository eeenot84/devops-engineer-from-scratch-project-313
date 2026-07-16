#!/bin/sh
set -eu

PORT="${PORT:-80}"
export PORT

envsubst '${PORT}' < /app/nginx.conf.template > /tmp/nginx.conf

# Backend на внутреннем порту; наружу слушает только Nginx
gunicorn --bind 127.0.0.1:8000 --workers 2 --timeout 30 main:app &
GUNICORN_PID=$!

cleanup() {
  kill "$GUNICORN_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Небольшая пауза, чтобы gunicorn успел подняться
sleep 1

exec nginx -g 'daemon off;' -c /tmp/nginx.conf
