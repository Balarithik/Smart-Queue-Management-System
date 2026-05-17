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
| [`docker-compose.yml`](docker-compose.yml) | Development: `db` + `backend`; optional `frontend` via profile `dev` |
| [`docker-compose.prod.yml`](docker-compose.prod.yml) | Production: `db` + Gunicorn `backend` + Nginx `nginx` |
| [`deploy/`](deploy/) | Nginx configs, production web Dockerfile |

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
| `/api/reports/platform/?days=30` | GET | `ADMIN` only — platform dashboard (users, orgs, queues, activity) |

Create an **admin** user (including `ADMIN` role) via Django:

```bash
cd backend
python manage.py createsuperuser
```

Then set **`role`** to **`ADMIN`** in the Django admin **Users** screen if needed.

The React app stores tokens in **`localStorage`**, attaches **`Authorization: Bearer`** on API calls, and refreshes access tokens on **401** via [`frontend/src/api/client.ts`](frontend/src/api/client.ts). Protected UI routes wrap [`ProtectedRoute`](frontend/src/components/ProtectedRoute.tsx).

### Running tests

From `backend/` (with venv activated):

```bash
python manage.py test accounts organizations queues reports config
```

Queue image upload and search API tests live under **`queues.tests`** (`test_queue_image`, `test_queue_search`, `test_queue_flow`). Example:

```bash
python manage.py test queues
```

Critical production paths are covered in **`config.tests`** (health probe, register/login/refresh, full queue join → call next journey) plus existing **`accounts`** and **`queues`** suites.

### Organizations

Each **`ORGANIZATION`** or **`ADMIN`** user may own **one** [`organizations.Organization`](backend/organizations/models.py) record (`owner` is a **OneToOne** with [`accounts.User`](backend/accounts/models.py)). [`queues.Queue`](backend/queues/models.py) rows belong to an organization (`slug` unique per organization).

| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/organizations/` | POST | Bearer token; **`ORGANIZATION`** or **`ADMIN`** — create organization (`name`, optional `slug`, optional `description`) |
| `/api/organizations/me/` | GET | Bearer token; **`ORGANIZATION`** or **`ADMIN`** — current user’s organization (**404** if none) |
| `/api/organizations/<id>/queues/` | GET | Bearer token; organization **owner** or **`ADMIN`** — list queues (each row includes **`join_url`**, **`qr_image_url`**, **`qr_png_base64`**) |
| `/api/organizations/<id>/stats/` | GET | Bearer token; organization **owner** or **`ADMIN`** — `queue_count`, `active_queue_count` |

React routes (organization-focused UX):

| Route | Purpose |
|-------|---------|
| `/org/register` | Register with role **`ORGANIZATION`** (links to standard registration API) |
| `/org/login` | Sign in; defaults redirect to **`/org/dashboard`** |
| `/org/dashboard` | **`ORGANIZATION`** / **`ADMIN`** only — load or create organization, stats, queue list with **banner** (`image_url`) and **QR thumbnails** (`qr_image_url`) |
| `/dashboard` | Authenticated — **`USER`**: search/join catalog via **`/api/queues/search/`** with live status polling; other roles see account shortcuts |

### Queue management

Queues use a stable **`public_id`** (UUID) for join URLs and QR codes. **[`queues.QueueEntry`](backend/queues/models.py)** stores each customer ticket (`token` sequence) and **`WAITING` / `CALLED` / `COMPLETED`** status. Join and **call next** use **`transaction.atomic()`** with **`select_for_update()`** on the [`Queue`](backend/queues/models.py) row (and entries when advancing).

Set **`FRONTEND_ORIGIN`** in `.env` (see [`backend/config/settings/base.py`](backend/config/settings/base.py)) so QR codes embed the correct SPA join URL (`{FRONTEND_ORIGIN}/join/{queue_public_id}`).

Each queue’s QR PNG is written under **`MEDIA_ROOT/qr/<public_id>.png`** (via the **`qrcode`** library). Optional banner images are stored under **`MEDIA_ROOT/queues/<public_id>/`** (JPEG/PNG, max size **`QUEUE_IMAGE_MAX_BYTES`** in [`.env.example`](.env.example), default 2 MB). In **`DEBUG`**, [`config/urls.py`](backend/config/urls.py) serves **`/media/`** so **`qr_image_url`** and **`image_url`** load in the browser. Production Nginx serves **`/media/`** from disk ([`deploy/nginx/sqms-docker.conf`](deploy/nginx/sqms-docker.conf)).

| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/queues/` | POST | Bearer; **`ORGANIZATION`** or **`ADMIN`** — create queue (`name`, optional `slug`, optional **`image`** file; admins send `organization_id`) — JSON or **multipart/form-data**; response includes **`join_url`**, **`qr_image_url`**, **`image_url`**, **`qr_png_base64`** |
| `/api/queues/search/?q=&page=&page_size=&is_active=` | GET | Public — paginated catalog (`public_id`, `name`, `organization_name`, `image_url`, `queue_status`, `waiting_count`) |
| `/api/queues/<uuid>/` | GET | Public — queue name / active flag |
| `/api/queues/<uuid>/manage/` | GET | Bearer; queue org **owner** or **`ADMIN`** — staff detail + **`join_url`**, **`qr_image_url`**, **`qr_png_base64`** |
| `/api/queues/<uuid>/join/` | POST | Public — issue token; returns **`token`**, **`waiting_ahead`** |
| `/api/queues/<uuid>/status/?token=` | GET | Public — realtime snapshot: **`current_token`**, **`position`**, **`eta_seconds`**, **`queue_status`**, **`waiting_ahead`**, entry **`status`** (poll every 10s) |
| `/api/queues/<uuid>/next/` | POST | Bearer; owner or **`ADMIN`** — call next **`WAITING`** token (**`select_for_update`**) |
| `/api/queues/<uuid>/dashboard/` | GET | Bearer; owner or **`ADMIN`** — waiting counts, latest tokens, QR |

React routes:

| Route | Purpose |
|-------|---------|
| `/queues/create` | **`ORGANIZATION`** / **`ADMIN`** — create queue (optional banner image upload), then redirect to QR |
| `/queues/:publicId/qr` | Operator — show join URL + QR |
| `/queues/:publicId/dashboard` | Operator — live stats and **Call next** |
| `/join/:publicId` | Public — join queue; auto-refresh status every **10 seconds** |

### UX shell (frontend)

On first load the SPA shows a branded **splash screen** (~1.5s minimum, until auth bootstrap completes). Shared components: [`ErrorBoundary`](frontend/src/components/ErrorBoundary.tsx), [`SplashScreen`](frontend/src/components/SplashScreen.tsx), [`LoadingScreen`](frontend/src/components/LoadingScreen.tsx). List cards use **Framer Motion** for light enter/expand animations.

### Real-time updates

Polling-based updates today; WebSockets can be added later without changing the API contract.

- **[`queues/realtime.py`](backend/queues/realtime.py)** — `build_queue_status_snapshot()` (single source of truth for status fields), ETA from recent completed entries, `QueueUpdatePublisher` stub for future Channels/ASGI pushes.
- **`GET /api/queues/<uuid>/status/?token=`** — returns `current_token`, `position`, `eta_seconds`, `queue_status` (`OPEN` / `CLOSED`), `waiting_ahead`, `waiting_count`, `updated_at`, plus backward-compatible fields.
- **React** — [`useQueueStatus`](frontend/src/hooks/useQueueStatus.ts) and [`usePolling`](frontend/src/hooks/usePolling.ts) with **`POLL_INTERVAL_MS = 10_000`** on [`JoinQueue`](frontend/src/pages/JoinQueue.tsx) and the operator dashboard.

### Notifications

The **`notifications`** app provides an abstraction layer and queue integration hooks:

- **[`notifications/services.py`](backend/notifications/services.py)** — `NotificationChannel` (abstract), placeholder **`EmailNotificationChannel`**, **`SmsNotificationChannel`**, **`PushNotificationChannel`**, **`NotificationOrchestrator`**, and **`NotificationContext`** / **`NotificationEvent`**.
- **[`notifications/hooks.py`](backend/notifications/hooks.py)** — `notify_user_joined_queue`, `notify_user_became_active`, `notify_queue_closed` (call from other apps).
- **Triggers**: **`join_queue`** schedules **`user_joined_queue`** on **`transaction.on_commit`**; **`QueueNextView`** calls **`user_became_active`** after a token is **`CALLED`**; **`Queue.is_active`** **True → False** schedules **`queue_closed`** via **[`notifications/signals.py`](backend/notifications/signals.py)** (also **`on_commit`**).

Optional env vars for future **SendGrid** / **Twilio** / **FCM** wiring are in [`.env.example`](.env.example) and [`backend/config/settings/base.py`](backend/config/settings/base.py). Run **`python manage.py test notifications`**.

### Production build (frontend)

Set `VITE_API_BASE_URL` to your deployed API origin (no trailing slash), then:

```bash
cd frontend
npm run build
```

Output is written to `frontend/dist/`.

## Production deployment

### Architecture

| Tier | Technology | Role |
|------|------------|------|
| API | **Gunicorn** + Django | REST API, admin, WhiteNoise **`/static/`** |
| App DB | **PostgreSQL** | Required when `DJANGO_SETTINGS_MODULE=config.settings.production` |
| Web | **Nginx** | Serves React **`frontend/dist`**, proxies **`/api/`**, **`/admin/`**, **`/static/`**; serves **`/media/`** (QR images) from disk |
| Process | **Docker Compose** | [`docker-compose.prod.yml`](docker-compose.prod.yml) — `db` + `backend` + `nginx` |

Configuration files:

- [`backend/gunicorn.conf.py`](backend/gunicorn.conf.py) — workers, timeout, bind (override via `GUNICORN_*` env vars)
- [`deploy/nginx/sqms.conf`](deploy/nginx/sqms.conf) — example bare-metal Nginx site
- [`deploy/nginx/sqms-docker.conf`](deploy/nginx/sqms-docker.conf) — Nginx config for Compose prod stack
- [`deploy/Dockerfile.nginx`](deploy/Dockerfile.nginx) — builds SPA + Nginx image
- [`deploy/README.md`](deploy/README.md) — quick reference

### Environment variables (production)

Copy [`.env.example`](.env.example) to `.env` and set at minimum:

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Long random string (**required** in production) |
| `DATABASE_URL` | PostgreSQL URL (**required** in production) |
| `ALLOWED_HOSTS` | Comma-separated API hostnames |
| `CORS_ALLOWED_ORIGINS` | SPA origins allowed to call the API with credentials |
| `CSRF_TRUSTED_ORIGINS` | Same origins for Django CSRF (admin forms) |
| `FRONTEND_ORIGIN` | Public SPA URL for QR join links (no trailing slash) |
| `VITE_API_BASE_URL` | Browser-visible API URL when building the frontend (often same origin as SPA, e.g. `http://localhost` or `https://app.example.com`) |
| `SECURE_SSL_REDIRECT` | `True` when HTTPS is terminated in front of Django |

Optional: `GUNICORN_WORKERS`, `GUNICORN_TIMEOUT`, notification provider keys (see `.env.example`).

### Health check

`GET /api/health/` returns **200** when the database is reachable:

```json
{"status": "ok", "service": "smart-queue-api", "checks": {"database": "ok"}}
```

Returns **503** if the database check fails (used by Docker healthchecks and load balancers).

### Docker Compose (production stack)

```bash
copy .env.example .env
# Edit SECRET_KEY, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, FRONTEND_ORIGIN, VITE_API_BASE_URL

docker compose -f docker-compose.prod.yml up --build
```

- Application: [http://localhost](http://localhost) (port **`NGINX_HTTP_PORT`**, default **80**)
- API (internal): Gunicorn on `backend:8000`
- Media volume: shared between `backend` and `nginx` for `/media/qr/`

### Bare-metal / VM

1. Install PostgreSQL, Python 3.12+, Node 20+, Nginx.
2. Deploy backend: `pip install -r requirements.txt`, `migrate`, `collectstatic`, run Gunicorn:

   ```bash
   cd backend
   export DJANGO_SETTINGS_MODULE=config.settings.production
   gunicorn -c gunicorn.conf.py
   ```

3. Build frontend with `VITE_API_BASE_URL` set to your public URL.
4. Copy `frontend/dist` → `/var/www/sqms/frontend`, mount `MEDIA_ROOT` at `/var/www/sqms/media`.
5. Enable [`deploy/nginx/sqms.conf`](deploy/nginx/sqms.conf) (adjust `upstream` and paths).

### Security and static/media

- **Production settings** ([`config/settings/production.py`](backend/config/settings/production.py)): `DEBUG=False`, strong `SECRET_KEY`, PostgreSQL required, secure cookies when `SECURE_SSL_REDIRECT=True`, HSTS optional, XSS/MIME/frame protections.
- **CORS**: `django-cors-headers` — set explicit origins; no wildcard with credentials.
- **Static files**: collected to `staticfiles/`; served via **WhiteNoise** through Gunicorn (`/static/`).
- **Media files**: not served by Django in production; **Nginx** serves `/media/` from the shared volume/path (QR PNGs).

## Docker Compose (development)

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

- **accounts** — custom user model and JWT authentication.
- **organizations** — tenant **`Organization`** model and REST API (`/api/organizations/`).
- **queues** — **`Queue`** + **`QueueEntry`**, join/next APIs, QR generation (`qrcode`, `Pillow`).
- **notifications** — abstract notification layer ([`services.py`](backend/notifications/services.py)), integration hooks ([`hooks.py`](backend/notifications/hooks.py)), queue close signal ([`signals.py`](backend/notifications/signals.py)).
- **reports** — analytics schema (`DailyQueueMetric`, `DailyOrganizationMetric`), aggregation services, and REST APIs:
  - `GET /api/reports/organizations/<pk>/?days=30` — org stats, daily series, per-queue breakdown (org owner or admin).
  - `GET /api/reports/queues/<public_id>/?days=30` — queue stats, status breakdown, avg wait (org owner or admin).
  - `GET /api/reports/users/` — platform user stats by role and signups (admin only).
  - `GET /api/reports/platform/?days=30` — unified platform admin dashboard (admin only).
  - SPA route **`/org/reports`** — Recharts analytics dashboard for organization users.
  - SPA route **`/admin/dashboard`** — **`ADMIN`** only — platform monitoring (users, orgs, queues, charts).

### Admin monitoring

Platform administrators (`role=ADMIN`) can view cross-tenant metrics without listing every organization separately.

| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/reports/platform/?days=30` | GET | Bearer token; **`ADMIN`** only — `users`, `organizations.total`, `queues` (totals, active, entry status), `daily_series` |

Create an admin user via `createsuperuser` and set **`role`** to **`ADMIN`** in Django admin. Sign in on the SPA and open **`/admin/dashboard`** (also linked in the nav for admin users). Admins may still use org routes (`/org/dashboard`, queue tools) when needed.

## Configuration notes

- **QR join URLs**: Set **`FRONTEND_ORIGIN`** so QR codes point at your SPA (same file as other env vars).
- **CORS**: Configured via `django-cors-headers` and `CORS_ALLOWED_ORIGINS` (see [`backend/config/settings/base.py`](backend/config/settings/base.py)).
- **Static files**: Development uses Django staticfiles storage; production uses **WhiteNoise** compressed manifests (see [`production.py`](backend/config/settings/production.py)).
- **Logging**: Console logging with level `LOG_LEVEL` (default `INFO`). Django logs **`Forbidden`** (HTTP **403**) on the **`django.request`** logger at **WARNING** when the authenticated user’s **role** is not allowed for that path. The SPA re-syncs **`/api/accounts/me/`** when **`localStorage`** tokens change in **another tab** (`storage` event) and on **window focus** (debounced) so React **`user.role`** matches the active JWT and org-only routes are not mounted for a **USER** token.

## License

Specify your license here.
