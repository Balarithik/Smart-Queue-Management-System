from django.db import models
from apps.queues.models import Service


class AnalyticsRecord(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="analytics_records")
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField(db_index=True)
    avg_wait_minutes = models.FloatField(default=0)
    throughput = models.PositiveIntegerField(default=0)
    abandonment_rate = models.FloatField(default=0)

    class Meta:
        indexes = [models.Index(fields=["service", "period_start"])]
