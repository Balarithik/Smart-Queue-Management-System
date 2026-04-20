import uuid
from django.conf import settings
from django.db import models
from apps.organizations.models import AgentCounter, Organization


class Service(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=120)
    code = models.SlugField(max_length=32)
    average_service_minutes = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "code")
        indexes = [models.Index(fields=["organization", "is_active"])]


class QueueEntry(models.Model):
    class Status(models.TextChoices):
        WAITING = "waiting", "Waiting"
        CALLED = "called", "Called"
        SERVING = "serving", "Serving"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="queue_entries")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="queue_entries")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING, db_index=True)
    position = models.PositiveIntegerField(default=1)
    estimated_wait_minutes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["service", "status", "created_at"]),
            models.Index(fields=["user", "status"]),
        ]


class Ticket(models.Model):
    queue_entry = models.OneToOneField(QueueEntry, on_delete=models.CASCADE, related_name="ticket")
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    token = models.CharField(max_length=12, db_index=True)
    counter = models.ForeignKey(AgentCounter, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets")
    called_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["token"])]
