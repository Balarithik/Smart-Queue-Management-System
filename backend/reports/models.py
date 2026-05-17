from django.db import models


class DailyQueueMetric(models.Model):
    """Pre-aggregated daily metrics for a single queue."""

    queue = models.ForeignKey(
        "queues.Queue",
        on_delete=models.CASCADE,
        related_name="daily_metrics",
    )
    date = models.DateField()
    joins = models.PositiveIntegerField(default=0)
    called = models.PositiveIntegerField(default=0)
    completed = models.PositiveIntegerField(default=0)
    peak_waiting = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-date",)
        constraints = [
            models.UniqueConstraint(
                fields=("queue", "date"),
                name="reports_dailyqueuemetric_queue_date_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["queue", "date"]),
            models.Index(fields=["date"]),
        ]

    def __str__(self) -> str:
        return f"{self.queue_id}@{self.date}"


class DailyOrganizationMetric(models.Model):
    """Pre-aggregated daily metrics for an organization."""

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="daily_metrics",
    )
    date = models.DateField()
    total_joins = models.PositiveIntegerField(default=0)
    total_completed = models.PositiveIntegerField(default=0)
    active_queues = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-date",)
        constraints = [
            models.UniqueConstraint(
                fields=("organization", "date"),
                name="reports_dailyorgmetric_org_date_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["organization", "date"]),
            models.Index(fields=["date"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization_id}@{self.date}"
