# Production deployment assets

| File | Purpose |
|------|---------|
| [`nginx/sqms.conf`](nginx/sqms.conf) | Example Nginx site for a bare-metal / VM install |
| [`nginx/sqms-docker.conf`](nginx/sqms-docker.conf) | Nginx config used by `docker-compose.prod.yml` |
| [`nginx/frontend-spa.conf`](nginx/frontend-spa.conf) | SPA-only Nginx (static hosting without API proxy) |
| [`Dockerfile.nginx`](Dockerfile.nginx) | Multi-stage image: Vite build + Nginx reverse proxy |

## Docker (recommended)

From the repository root:

```bash
copy .env.example .env
docker compose -f docker-compose.prod.yml up --build
```

Open `http://localhost` (port `NGINX_HTTP_PORT` in `.env`).

## Bare metal

1. Build the frontend: `cd frontend && npm ci && VITE_API_BASE_URL=https://your-domain npm run build`
2. Copy `frontend/dist` to `/var/www/sqms/frontend`
3. Set `MEDIA_ROOT` on the host (or volume) at `/var/www/sqms/media`
4. Run Gunicorn with `backend/gunicorn.conf.py` and `DJANGO_SETTINGS_MODULE=config.settings.production`
5. Install [`nginx/sqms.conf`](nginx/sqms.conf) and reload Nginx

See the main [README.md](../README.md) for environment variables and security notes.
