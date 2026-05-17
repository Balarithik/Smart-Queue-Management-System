from django.contrib import admin

from reports.models import DailyOrganizationMetric, DailyQueueMetric


@admin.register(DailyQueueMetric)
class DailyQueueMetricAdmin(admin.ModelAdmin):
    list_display = ("queue", "date", "joins", "called", "completed", "peak_waiting")
    list_filter = ("date",)
    search_fields = ("queue__name", "queue__slug")


@admin.register(DailyOrganizationMetric)
class DailyOrganizationMetricAdmin(admin.ModelAdmin):
    list_display = ("organization", "date", "total_joins", "total_completed", "active_queues")
    list_filter = ("date",)
    search_fields = ("organization__name", "organization__slug")
