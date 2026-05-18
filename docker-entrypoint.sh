#!/bin/sh
set -e

PORT="${PORT:-8080}"
export PORT

# Nginx listens on $PORT (Render injects PORT, e.g. 10000). Gunicorn uses GUNICORN_BIND.
sed "s/__PORT__/${PORT}/g" /app/deploy/nginx/render-docker.conf.template > /etc/nginx/conf.d/default.conf

cd /app/backend
python manage.py migrate --noinput

gunicorn wsgi:application --config gunicorn.conf.py &
GUNICORN_PID=$!
trap 'kill "$GUNICORN_PID" 2>/dev/null; exit 0' EXIT TERM INT

exec nginx -g "daemon off;"
