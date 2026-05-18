# =============================================================================
# All-in-one image: Vite SPA + Django (Gunicorn) + Nginx reverse proxy
# For Render: set runtime = Docker, Dockerfile path = ./Dockerfile, context = .
# Same-origin SPA → leave VITE_API_BASE_URL empty at build (relative /api).
# =============================================================================

# --- Frontend (Vite): same-origin API (empty VITE_API_BASE_URL) ---
FROM node:22-bookworm-slim AS frontend
WORKDIR /src
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

# --- Collect static (production settings + ephemeral sqlite) ---
FROM python:3.12-slim-bookworm AS backend-static
WORKDIR /app/backend
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY backend/ .
ARG COLLECTSTATIC_SECRET=build-only-collectstatic-secret-not-for-production
ENV DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=${COLLECTSTATIC_SECRET} \
    DATABASE_URL=sqlite:////tmp/docker-build-collectstatic.sqlite3
RUN python manage.py collectstatic --noinput

# --- Runtime: Nginx + Gunicorn + Django + SPA ---
FROM python:3.12-slim-bookworm
WORKDIR /app/backend

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend/ /app/backend/
COPY --from=frontend /src/dist /app/spa
COPY --from=backend-static /app/backend/staticfiles /app/backend/staticfiles

COPY deploy/nginx/render-docker.conf.template /app/deploy/nginx/render-docker.conf.template
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh \
    && chmod +x /docker-entrypoint.sh

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    GUNICORN_BIND=127.0.0.1:8000 \
    GUNICORN_WORKERS=2

EXPOSE 8080

ENTRYPOINT ["/docker-entrypoint.sh"]
