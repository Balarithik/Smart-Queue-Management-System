# Smart Queue Management System

Django REST API (`backend/`) and React + Vite SPA (`frontend/`) for queue management, QR join links, real-time polling, and admin analytics. Deploy on **[Render](https://render.com)** using either **native** (Python web + static site) or **Docker** (single image: Nginx + Gunicorn + SPA).

## Repository layout

| Path | Purpose |
|------|---------|
| [`backend/`](backend/) | Django project `config` — apps: `accounts`, `organizations`, `queues`, `notifications`, `reports` |
| [`frontend/`](frontend/) | Vite + React + TypeScript, Tailwind CSS v4 |
| [`Dockerfile`](Dockerfile) | **All-in-one** production image (build SPA + collectstatic + Nginx + Gunicorn) |
| [`docker-compose.yml`](docker-compose.yml) | Local stack: PostgreSQL + web image |
| [`docker-entrypoint.sh`](docker-entrypoint.sh) | Migrations, then Gunicorn + Nginx |
| [`deploy/nginx/render-docker.conf.template`](deploy/nginx/render-docker.conf.template) | Nginx routing for Docker / Render |
| [`Procfile`](Procfile) | Native Render: Gunicorn from repo root |
| [`render.yaml`](render.yaml) | Blueprint: native API + static site + Postgres |
| [`render.docker.yaml`](render.docker.yaml) | Blueprint: **Docker** web + Postgres |
| [`requirements.txt`](requirements.txt) | Root pointer to pinned [`backend/requirements.txt`](backend/requirements.txt) |

## Docker (complete app)

### What the image does

1. **Build** — `npm ci && npm run build` in `frontend` with **empty** `VITE_API_BASE_URL` so the browser calls **`/api/...`** on the same host (no CORS split).
2. **Collectstatic** — Django production settings + temporary SQLite (manifest only).
3. **Runtime** — **Nginx** listens on **`PORT`** (Render injects this, e.g. `10000`). It serves the SPA and proxies `/api/`, `/admin/`, `/static/`, `/media/` to **Gunicorn** on `127.0.0.1:8000`.

### Local run

```bash
docker compose up --build
```

- App: [http://localhost:8080](http://localhost:8080) (SPA + API same origin)
- Health: [http://localhost:8080/api/health/](http://localhost:8080/api/health/)

### Render (Docker web service)

1. **New → Web Service** → connect repo → **Runtime: Docker**.
2. **Dockerfile path:** `Dockerfile` · **Docker context:** `.` (repo root).
3. **Health check path:** `/api/health/`
4. Create **PostgreSQL** and set **`DATABASE_URL`** on the web service (or apply [`render.docker.yaml`](render.docker.yaml) as a Blueprint and fill `sync: false` variables).

**Required environment variables** (same as [`.env.example`](.env.example), adjusted for one public URL):

| Variable | Example |
|----------|---------|
| `SECRET_KEY` | Strong random string |
| `DATABASE_URL` | From Render Postgres (internal URL) |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `ALLOWED_HOSTS` | `your-service.onrender.com` |
| `FRONTEND_ORIGIN` | `https://your-service.onrender.com` (no trailing slash — used in QR links) |
| `CORS_ALLOWED_ORIGINS` | Same URL as `FRONTEND_ORIGIN` |
| `CSRF_TRUSTED_ORIGINS` | Same URL |
| `SECURE_SSL_REDIRECT` | `true` |
| `SERVE_MEDIA` | `true` |

Render sets **`PORT`** and usually **`RENDER_EXTERNAL_HOSTNAME`**; Django production settings still apply.

**Optional:** attach a **persistent disk** mounted at `/app/backend/media` if you need uploaded QR/banner files to survive redeploys.

### Build image only (CI / smoke test)

```bash
docker build -t sqms:local .
```

## Prerequisites (local)

- Python **3.12+**
- Node.js **20+**
- PostgreSQL (optional locally — SQLite works for development)

## Local development

### 1. Environment

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

For local API work, set `DEBUG=True`, `DJANGO_SETTINGS_MODULE=config.settings.development` (or omit — [`manage.py`](backend/manage.py) defaults to development), and leave `DATABASE_URL` empty to use SQLite.

### 2. Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Windows PowerShell
# source .venv/bin/activate           # macOS/Linux

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Health: [http://127.0.0.1:8000/api/health/](http://127.0.0.1:8000/api/health/)

### 3. Frontend

```bash
cd frontend
npm ci
npm run dev
```

- App: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- Vite proxies `/api` → `http://127.0.0.1:8000` ([`vite.config.ts`](frontend/vite.config.ts))
- Leave `VITE_API_BASE_URL` empty in dev

## Deploy on Render

You can deploy in **two** ways:

| Mode | When to use |
|------|-------------|
| **Native** | Separate Render **Web Service** (Python, `backend/`) + **Static Site** (`frontend/`) — see [`render.yaml`](render.yaml). |
| **Docker** | One **Web Service (Docker)** using root [`Dockerfile`](Dockerfile) — see [`render.docker.yaml`](render.docker.yaml). |

### Architecture (native — two Render services)

| Service | Render type | Root directory | Role |
|---------|-------------|----------------|------|
| **sqms-api** | Web (Python) | `backend` | Gunicorn + Django REST API, WhiteNoise `/static/`, optional `/media/` when `SERVE_MEDIA=true` |
| **sqms-web** | Static Site | `frontend` | `npm run build` → `dist/` |
| **sqms-db** | PostgreSQL | — | `DATABASE_URL` for the API |

### Architecture (Docker — one Render service)

| Service | Role |
|---------|------|
| **Single web (Docker)** | Nginx (`PORT`) + Gunicorn + built SPA + Django API |

### Quick setup (native, dashboard)

**API (Web Service)**

- **Root Directory:** `backend`
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn wsgi:application --config gunicorn.conf.py`
- **Health Check Path:** `/api/health/`
- **Environment:** see [`.env.example`](.env.example) — at minimum `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `FRONTEND_ORIGIN`, `SECURE_SSL_REDIRECT=true`, `SERVE_MEDIA=true`, `DJANGO_SETTINGS_MODULE=config.settings.production`

Render injects `PORT` and `RENDER_EXTERNAL_HOSTNAME`; production settings append the hostname to `ALLOWED_HOSTS` and enable HTTPS defaults.

**Frontend (Static Site)**

- **Root Directory:** `frontend`
- **Build Command:** `npm ci && npm run build`
- **Publish Directory:** `dist`
- **Environment (build-time):** `VITE_API_BASE_URL=https://<your-api-host>.onrender.com`

SPA routing uses [`frontend/public/_redirects`](frontend/public/_redirects) (`/* /index.html 200`).

### Blueprint

- **Native:** [`render.yaml`](render.yaml) — API + static site + Postgres; set `ALLOWED_HOSTS`, `CORS_*`, `FRONTEND_ORIGIN`, `VITE_API_BASE_URL` after first deploy.
- **Docker:** [`render.docker.yaml`](render.docker.yaml) — one Docker web service + Postgres; set `ALLOWED_HOSTS`, `CORS_*`, `FRONTEND_ORIGIN` to your **single** public URL (same host for SPA and API).

```bash
# Native blueprint — connect repo and apply render.yaml
# Docker blueprint — apply render.docker.yaml (or rename/copy as render.yaml)
```

Or use the repo-root [`Procfile`](Procfile) if you run the API from the **repository root** (not from `backend/`).

### Media on Render

QR codes and queue banner images are stored under `backend/media/`. With `SERVE_MEDIA=true`, Django serves `/media/` (no separate Nginx). Render’s filesystem is **ephemeral** unless you attach a persistent disk — plan for object storage for production-scale media if needed.

## Running tests

From `backend/` with venv activated:

```bash
python manage.py test accounts organizations queues reports notifications config
```

Queue-specific suites:

```bash
python manage.py test queues
```

## API overview

### Authentication (JWT)

| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/accounts/register/` | POST | Public |
| `/api/accounts/token/` | POST | Public |
| `/api/accounts/token/refresh/` | POST | Public |
| `/api/accounts/me/` | GET | Bearer |

Roles: `USER`, `ORGANIZATION`, `ADMIN`.

### Organizations & queues

| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/organizations/` | POST | `ORGANIZATION` / `ADMIN` |
| `/api/organizations/me/` | GET | `ORGANIZATION` / `ADMIN` |
| `/api/organizations/<id>/queues/` | GET | Owner / `ADMIN` |
| `/api/queues/` | POST | `ORGANIZATION` / `ADMIN` (JSON or multipart + optional `image`) |
| `/api/queues/search/` | GET | Public — paginated catalog |
| `/api/queues/<uuid>/join/` | POST | Public |
| `/api/queues/<uuid>/status/?token=` | GET | Public — poll every 10s |
| `/api/queues/<uuid>/next/` | POST | Owner / `ADMIN` |
| `/api/reports/platform/?days=30` | GET | `ADMIN` |

### React routes

| Route | Purpose |
|-------|---------|
| `/` | Redirect: login if signed out; role home if signed in |
| `/dashboard` | User search + join (`USER` only) |
| `/org/dashboard` | Organization queues + QR/images |
| `/queues/create` | Create queue (optional banner) |
| `/join/:publicId` | Public join + live status |
| `/admin/dashboard` | Platform metrics (`ADMIN`) |

## Configuration reference

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django secret (required in production) |
| `DATABASE_URL` | PostgreSQL URL (required in production) |
| `ALLOWED_HOSTS` | API hostnames (comma-separated) |
| `CORS_ALLOWED_ORIGINS` | SPA origins for API calls |
| `CSRF_TRUSTED_ORIGINS` | HTTPS origins for admin |
| `FRONTEND_ORIGIN` | SPA URL for QR join links |
| `VITE_API_BASE_URL` | API URL baked into **native** static build; leave empty for **Docker** all-in-one (same origin) |
| `SERVE_MEDIA` | Serve `/media/` from Django (default on Render) |
| `SECURE_SSL_REDIRECT` | Force HTTPS (default on Render) |
| `QUEUE_IMAGE_MAX_BYTES` | Max banner upload size (default 2 MB) |

## Backend apps

- **accounts** — custom user model, JWT
- **organizations** — tenant organizations
- **queues** — queues, entries, QR, search, realtime status
- **notifications** — hook layer (email/SMS/push placeholders)
- **reports** — analytics and admin platform dashboard

## License

Specify your license here.
