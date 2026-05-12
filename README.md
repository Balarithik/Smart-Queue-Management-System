# Smart Queue Management System

Monorepo skeleton: Django API (`backend/`), React + Vite SPA (`frontend/`), and Docker Compose for PostgreSQL plus optional containerized dev workflows.

## Prerequisites

- Python **3.12+**
- Node.js **20+** (project tested with Node 22 via the frontend Docker image)
- **PostgreSQL** when not using SQLite (Compose provides Postgres **16**)

## Repository layout

| Path | Purpose |
|------|---------|
| [`backend/`](backend/) | Django project `config` with apps: `accounts`, `organizations`, `queues`, `notifications`, `reports` |
| [`backend/config/settings/`](backend/config/settings/) | Shared `base.py`, `development.py`, `production.py` |
| [`frontend/`](frontend/) | Vite + React + TypeScript, Tailwind CSS v4, React Router v6, Axios |
| [`docker-compose.yml`](docker-compose.yml) | `db` + `backend`; optional `frontend` via profile `dev` |

## Local development (without Docker)

### Backend

Use a **virtual environment** so dependencies (including **`django-environ`**, imported as `environ`) are installed for this project—not only your global Python.

From the **repository root**, copy environment defaults once:

```bash
copy .env.example .env   # Windows; use cp on Unix
```

Then create the venv, install requirements, migrate, and run:

```bash
cd backend
python -m venv .venv
# Windows (PowerShell): .\.venv\Scripts\Activate.ps1
# Windows (cmd): .venv\Scripts\activate.bat
# macOS/Linux: source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Always **activate `.venv`** before `manage.py` in a new terminal. If you see **`ModuleNotFoundError: No module named 'environ'`**, you are not using the venv or you skipped `pip install -r requirements.txt`.

- Settings module defaults to **`config.settings.development`** (see [`manage.py`](backend/manage.py)).
- Without `DATABASE_URL`, Django uses **`backend/db.sqlite3`**.
- Health check: [http://127.0.0.1:8000/api/health/](http://127.0.0.1:8000/api/health/)

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

- Dev server: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- [`vite.config.ts`](frontend/vite.config.ts) proxies **`/api`** → `http://localhost:8000`.
- Leave `VITE_API_BASE_URL` empty in dev so Axios calls like `/api/health/` go through the proxy.

### Authentication (JWT)

The API uses **django-rest-framework-simplejwt**. The custom user model lives in **`accounts.User`** with **`role`**: `USER`, `ORGANIZATION`, or `ADMIN`.

| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/accounts/register/` | POST | Public (`USER` or `ORGANIZATION`; `ADMIN` not self-service) |
| `/api/accounts/token/` | POST | Public (login; returns `access` + `refresh`) |
| `/api/accounts/token/refresh/` | POST | Public (body: `{ "refresh": "<token>" }`) |
| `/api/accounts/me/` | GET | Bearer access token |
| `/api/accounts/admin/ping/` | GET | `ADMIN` only |
| `/api/accounts/organization/ping/` | GET | `ORGANIZATION` or `ADMIN` |

Create an **admin** user (including `ADMIN` role) via Django:

```bash
cd backend
python manage.py createsuperuser
```

Then set **`role`** to **`ADMIN`** in the Django admin **Users** screen if needed.

The React app stores tokens in **`localStorage`**, attaches **`Authorization: Bearer`** on API calls, and refreshes access tokens on **401** via [`frontend/src/api/client.ts`](frontend/src/api/client.ts). Protected UI routes wrap [`ProtectedRoute`](frontend/src/components/ProtectedRoute.tsx).

Backend tests: `python manage.py test accounts`.

### Production build (frontend)

Set `VITE_API_BASE_URL` to your deployed API origin (no trailing slash), then:

```bash
cd frontend
npm run build
```

Output is written to `frontend/dist/`.

## Docker Compose

From the repository root (after copying `.env.example` → `.env` and setting `SECRET_KEY` for anything beyond local experiments):

```bash
docker compose up --build
```

- API: [http://localhost:8000](http://localhost:8000) — includes **`DJANGO_SETTINGS_MODULE=config.settings.production`**, PostgreSQL, and migrations run on container start.
- Postgres is exposed on **`5432`** by default (override `POSTGRES_PORT` in `.env`).

Optional **frontend** dev server in Docker (hot reload; profile **`dev`**):

```bash
docker compose --profile dev up --build
```

Frontend container exposes **`5173`** and sets `VITE_API_BASE_URL` (defaults to `http://localhost:8000` so the browser on your host can reach the mapped backend port).

### Postgres role / password errors (`role "sqms" does not exist`, authentication failed)

Compose only runs Postgres **initialization** on an **empty** data directory. If the named volume already contained a cluster from an older setup (or different `POSTGRES_USER` / `POSTGRES_PASSWORD`), the server skips init and your new credentials never create the `sqms` role—while Django still connects as `sqms` from `DATABASE_URL`.

**Fix:** reset the database volume, then start again:

```bash
docker compose down -v
docker compose up --build
```

`-v` removes the Compose-managed Postgres volume so the next start runs initdb with the current `POSTGRES_*` values. After pulling changes that bump the Postgres volume name in `docker-compose.yml`, a fresh volume is created automatically; you can still remove orphan old volumes with `docker volume ls` / `docker volume rm` if you want to reclaim disk space.

Ensure `DATABASE_URL` matches `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` (defaults are aligned in [`.env.example`](.env.example)).

### `Not Found: /` or old code inside the container

Compose often **reuses cached image layers**. If you changed Python/Django files but still see **404 on `/`** or old behavior, rebuild the backend image without cache:

```bash
docker compose build --no-cache backend
docker compose up
```

### Gunicorn `WORKER TIMEOUT` / `Error handling request (no URI read)`

On some setups (especially **Docker Desktop on Windows**), idle or half-open TCP connections to port **8000** can block Gunicorn’s sync workers until the default **30s** timeout, which kills workers and may log **SIGKILL / out of memory**.

The backend image sets a **longer `--timeout`**, fewer workers, and logs to stdout (see [`backend/Dockerfile`](backend/Dockerfile)). If problems persist, avoid leaving unknown tools polling `localhost:8000`, and restart the stack after rebuilding.

### Running Django management commands in Docker

```bash
docker compose exec backend python manage.py createsuperuser
```

(`manage.py` defaults to development settings; Compose sets `DJANGO_SETTINGS_MODULE` to production for the container.)

## Backend apps (modules)

- **accounts** — users and authentication extensions (placeholder).
- **organizations** — tenants / org structure (placeholder).
- **queues** — queue logic (placeholder).
- **notifications** — outbound notifications (placeholder).
- **reports** — reporting (placeholder).

Each app exposes an empty route include under `/api/<app>/` ready for future endpoints.

## Configuration notes

- **CORS**: Configured via `django-cors-headers` and `CORS_ALLOWED_ORIGINS` (see [`backend/config/settings/base.py`](backend/config/settings/base.py)).
- **Static files**: Development uses Django staticfiles storage; production uses **WhiteNoise** compressed manifests (see [`production.py`](backend/config/settings/production.py)).
- **Logging**: Console logging with level `LOG_LEVEL` (default `INFO`).

## License

Specify your license here.
