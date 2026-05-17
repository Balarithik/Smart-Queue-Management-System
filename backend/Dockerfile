FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG COLLECTSTATIC_SECRET=build-only-collectstatic-secret-not-for-production
ENV DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=${COLLECTSTATIC_SECRET}

RUN chmod +x docker-entrypoint.sh \
    && sed -i 's/\r$//' docker-entrypoint.sh \
    && DATABASE_URL=sqlite:////tmp/build.sqlite3 python manage.py collectstatic --noinput

ENTRYPOINT ["/app/docker-entrypoint.sh"]
# Fewer workers + higher timeout: Docker Desktop / stray TCP probes can otherwise hit
# Gunicorn's default 30s worker timeout ("WORKER TIMEOUT", "no URI read").
CMD ["gunicorn", "-c", "gunicorn.conf.py"]
