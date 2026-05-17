from django.db import connection
from django.http import JsonResponse


def root(request):
    return JsonResponse(
        {
            "service": "smart-queue-api",
            "message": "Smart Queue Management API",
            "endpoints": {
                "health": "/api/health/",
                "admin": "/admin/",
                "accounts": "/api/accounts/",
                "organizations": "/api/organizations/",
                "queues": "/api/queues/",
                "notifications": "/api/notifications/",
                "reports": "/api/reports/",
            },
        }
    )


def health(request):
    """Liveness/readiness probe: verifies database connectivity."""
    db_status = "ok"
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        db_status = "unavailable"

    healthy = db_status == "ok"
    payload = {
        "status": "ok" if healthy else "unavailable",
        "service": "smart-queue-api",
        "checks": {
            "database": db_status,
        },
    }
    return JsonResponse(payload, status=200 if healthy else 503)
