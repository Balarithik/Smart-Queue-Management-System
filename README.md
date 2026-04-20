# Smart Queue Management System

## File Structure
```text
backend/
  config/
  apps/{accounts,organizations,queues,analytics,notifications}/
  requirements/base.txt
  Dockerfile
frontend/
  src/app
  src/store
  src/features/{auth,queue,org,analytics,qr,notifications}
  src/tests
docs/
  analytics_queries.sql
  sample_curl.sh
docker-compose.yml
```

## API Schemas
```json
POST /api/v1/auth/login/
{ "username": "demo", "password": "Password123!" }
=> { "access": "jwt", "refresh": "jwt" }
```
```json
POST /api/v1/queues/entries/join/
{ "service": 1 }
=> { "id": 4, "status": "waiting", "position": 3, "estimated_wait_minutes": 15 }
```
```json
POST /api/v1/queues/entries/join_qr/
{ "organization_slug": "city-hospital", "service_code": "consult", "phone_number": "15550000002" }
=> { "id": 5, "status": "waiting", "position": 4, "estimated_wait_minutes": 20 }
```
```json
WS /ws/queues/{service_id}/
{ "type": "ticket.called", "timestamp": "2026-04-20T10:00:00Z", "payload": { "token": "CONSULT-0004" } }
```

## WhatsApp Templates (Meta Cloud API)
```text
queue_join_confirmation: "Ticket {{1}} confirmed. Position {{2}}. ETA {{3}} minutes."
queue_position_update: "Ticket {{1}} moved to position {{2}}. ETA {{3}} minutes."
queue_counter_call: "Ticket {{1}} please proceed to {{2}}. ETA {{3}} minutes."
```

## Migration and Seed
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
```

## TODO Checklist and Milestones
- [x] M1 bootstrap monorepo, infra config, auth foundation
- [x] M2 queue models, migrations, service and queue APIs
- [x] M3 websocket consumers, realtime tracker, UI animations
- [x] M4 QR generation/scanning and QR join endpoint
- [x] M5 WhatsApp integration with Celery dispatch
- [x] M6 analytics, CSV export, seed data, docs, CI

## Environment Variables
Use `.env.example` values for PostgreSQL, Redis, JWT, Django settings, and Meta WhatsApp credentials.
