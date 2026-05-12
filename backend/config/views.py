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
    return JsonResponse({"status": "ok", "service": "smart-queue-api"})
