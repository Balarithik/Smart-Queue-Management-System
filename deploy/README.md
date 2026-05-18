# Nginx + Docker (Render all-in-one)

The root [`Dockerfile`](../Dockerfile) copies [`nginx/render-docker.conf.template`](nginx/render-docker.conf.template) into the image. At container start, [`docker-entrypoint.sh`](../docker-entrypoint.sh) substitutes `__PORT__` with Render’s `PORT` and starts Nginx + Gunicorn.

- **`/api/`**, **`/admin/`**, **`/static/`**, **`/media/`** → Gunicorn (Django)
- **`/`** and client routes → static SPA (`/app/spa`)

For local testing use [`docker-compose.yml`](../docker-compose.yml) from the repository root.
