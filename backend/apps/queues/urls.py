from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import QueueViewSet, ServiceViewSet, ticket_pdf

router = DefaultRouter()
router.register("services", ServiceViewSet, basename="services")
router.register("entries", QueueViewSet, basename="queue-entries")

urlpatterns = router.urls + [
    path("tickets/<uuid:ticket_id>/print/", ticket_pdf, name="ticket-print"),
]
