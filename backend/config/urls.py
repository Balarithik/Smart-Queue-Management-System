from django.contrib import admin
from django.urls import include, path

from config.views import health, root

urlpatterns = [
    path("", root, name="root"),
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path("api/accounts/", include("accounts.urls")),
    path("api/organizations/", include("organizations.urls")),
    path("api/queues/", include("queues.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/reports/", include("reports.urls")),
]
