import uuid

from django.db import models


class Queue(models.Model):
    """A service queue belonging to an organization."""

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="queues",
    )
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    is_active = models.BooleanField(default=True)
    # Monotonic ticket counter; last number issued to a joining customer.
    last_token_issued = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("organization", "slug"),
                name="queues_queue_organization_slug_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.organization.slug}:{self.slug}"


class QueueEntry(models.Model):
    """One person's position in a queue."""

    class Status(models.TextChoices):
        WAITING = "WAITING", "Waiting"
        CALLED = "CALLED", "Called"
        COMPLETED = "COMPLETED", "Completed"

    queue = models.ForeignKey(
        Queue,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    token = models.PositiveIntegerField()
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.WAITING,
        db_index=True,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("token",)
        constraints = [
            models.UniqueConstraint(
                fields=("queue", "token"),
                name="queues_queueentry_queue_token_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.queue_id}:{self.token} ({self.status})"
