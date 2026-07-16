#!/bin/sh
set -eu

PORT="${PORT:-8080}"
export PORT

mkdir -p /tmp/nginx_client_body /tmp/nginx_proxy /tmp/nginx_fastcgi /tmp/nginx_uwsgi /tmp/nginx_scgi

envsubst '${PORT}' < /app/nginx.conf.template > /tmp/nginx.conf

echo "Starting gunicorn on 127.0.0.1:8000; nginx on PORT=${PORT}"

gunicorn --bind 127.0.0.1:8000 --workers 2 --timeout 30 main:app &
GUNICORN_PID=$!

cleanup() {
  kill "$GUNICORN_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Дождаться готовности backend
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if wget -q -O /dev/null "http://127.0.0.1:8000/ping" 2>/dev/null \
    || python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/ping')" 2>/dev/null; then
    break
  fi
  sleep 0.5
done

nginx -t -c /tmp/nginx.conf
exec nginx -g 'daemon off;' -c /tmp/nginx.conf
