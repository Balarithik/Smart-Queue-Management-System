from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from organizations.models import Organization
from queues.models import Queue, QueueEntry
from reports.models import DailyOrganizationMetric, DailyQueueMetric

User = get_user_model()

DEFAULT_DAYS = 30
MAX_DAYS = 365


def parse_days(raw: str | None) -> int:
    if raw is None or raw == "":
        return DEFAULT_DAYS
    try:
        days = int(raw)
    except (TypeError, ValueError):
        return DEFAULT_DAYS
    return max(1, min(days, MAX_DAYS))


def report_date_range(days: int) -> tuple[date, date]:
    end = timezone.localdate()
    start = end - timedelta(days=days - 1)
    return start, end


def _day_bounds(day: date) -> tuple[datetime, datetime]:
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime.combine(day, time.min), tz)
    end = timezone.make_aware(datetime.combine(day, time.max), tz)
    return start, end


def _peak_waiting_for_day(queue: Queue, day: date) -> int:
    _, day_end = _day_bounds(day)
    return (
        QueueEntry.objects.filter(queue=queue, joined_at__lte=day_end)
        .filter(Q(completed_at__isnull=True) | Q(completed_at__gt=day_end))
        .filter(
            status__in=[
                QueueEntry.Status.WAITING,
                QueueEntry.Status.CALLED,
            ]
        )
        .count()
    )


def refresh_daily_snapshots_for_queue(
    queue: Queue,
    start: date,
    end: date,
) -> None:
    current = start
    while current <= end:
        day_start, day_end = _day_bounds(current)
        joins = QueueEntry.objects.filter(
            queue=queue,
            joined_at__gte=day_start,
            joined_at__lte=day_end,
        ).count()
        called = QueueEntry.objects.filter(
            queue=queue,
            called_at__gte=day_start,
            called_at__lte=day_end,
        ).count()
        completed = QueueEntry.objects.filter(
            queue=queue,
            completed_at__gte=day_start,
            completed_at__lte=day_end,
        ).count()
        peak_waiting = _peak_waiting_for_day(queue, current)
        DailyQueueMetric.objects.update_or_create(
            queue=queue,
            date=current,
            defaults={
                "joins": joins,
                "called": called,
                "completed": completed,
                "peak_waiting": peak_waiting,
            },
        )
        current += timedelta(days=1)


def refresh_daily_snapshots_for_organization(
    org: Organization,
    days: int,
) -> None:
    start, end = report_date_range(days)
    queues = list(org.queues.all())
    for queue in queues:
        refresh_daily_snapshots_for_queue(queue, start, end)

    current = start
    while current <= end:
        day_start, day_end = _day_bounds(current)
        queue_ids = [q.pk for q in queues]
        if queue_ids:
            total_joins = QueueEntry.objects.filter(
                queue_id__in=queue_ids,
                joined_at__gte=day_start,
                joined_at__lte=day_end,
            ).count()
            total_completed = QueueEntry.objects.filter(
                queue_id__in=queue_ids,
                completed_at__gte=day_start,
                completed_at__lte=day_end,
            ).count()
        else:
            total_joins = 0
            total_completed = 0
        active_queues = org.queues.filter(is_active=True).count()
        DailyOrganizationMetric.objects.update_or_create(
            organization=org,
            date=current,
            defaults={
                "total_joins": total_joins,
                "total_completed": total_completed,
                "active_queues": active_queues,
            },
        )
        current += timedelta(days=1)


def _daily_series_from_snapshots(
    metrics: list[DailyQueueMetric],
    start: date,
    end: date,
) -> list[dict[str, Any]]:
    by_date = {m.date: m for m in metrics}
    series = []
    current = start
    while current <= end:
        m = by_date.get(current)
        series.append(
            {
                "date": current.isoformat(),
                "joins": m.joins if m else 0,
                "called": m.called if m else 0,
                "completed": m.completed if m else 0,
            }
        )
        current += timedelta(days=1)
    return series


def _aggregate_org_daily_series(
    org: Organization,
    start: date,
    end: date,
) -> list[dict[str, Any]]:
    metrics = (
        DailyOrganizationMetric.objects.filter(
            organization=org,
            date__gte=start,
            date__lte=end,
        )
        .order_by("date")
    )
    by_date = {m.date: m for m in metrics}
    series = []
    current = start
    while current <= end:
        m = by_date.get(current)
        series.append(
            {
                "date": current.isoformat(),
                "joins": m.total_joins if m else 0,
                "called": 0,
                "completed": m.total_completed if m else 0,
            }
        )
        current += timedelta(days=1)
    return series


def _entry_status_counts(queue_ids: list[int]) -> dict[str, int]:
    if not queue_ids:
        return {"waiting": 0, "called": 0, "completed": 0}
    qs = QueueEntry.objects.filter(queue_id__in=queue_ids)
    return {
        "waiting": qs.filter(status=QueueEntry.Status.WAITING).count(),
        "called": qs.filter(status=QueueEntry.Status.CALLED).count(),
        "completed": qs.filter(status=QueueEntry.Status.COMPLETED).count(),
    }


def get_org_report(org: Organization, days: int) -> dict[str, Any]:
    start, end = report_date_range(days)
    refresh_daily_snapshots_for_organization(org, days)

    queues = list(org.queues.all())
    queue_ids = [q.pk for q in queues]
    status_counts = _entry_status_counts(queue_ids)

    queue_summaries = []
    for queue in queues:
        metrics = list(
            DailyQueueMetric.objects.filter(
                queue=queue,
                date__gte=start,
                date__lte=end,
            )
        )
        total_joins = sum(m.joins for m in metrics)
        total_completed = sum(m.completed for m in metrics)
        queue_summaries.append(
            {
                "queue_id": queue.id,
                "public_id": str(queue.public_id),
                "name": queue.name,
                "slug": queue.slug,
                "is_active": queue.is_active,
                "joins": total_joins,
                "completed": total_completed,
            }
        )

    total_entries = sum(s["joins"] for s in queue_summaries)

    return {
        "organization_id": org.id,
        "name": org.name,
        "days": days,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "queue_count": len(queues),
        "active_queue_count": sum(1 for q in queues if q.is_active),
        "total_entries": total_entries,
        "waiting_count": status_counts["waiting"],
        "called_count": status_counts["called"],
        "completed_count": status_counts["completed"],
        "daily_series": _aggregate_org_daily_series(org, start, end),
        "queues": queue_summaries,
    }


def get_queue_report(queue: Queue, days: int) -> dict[str, Any]:
    start, end = report_date_range(days)
    refresh_daily_snapshots_for_queue(queue, start, end)

    metrics = list(
        DailyQueueMetric.objects.filter(
            queue=queue,
            date__gte=start,
            date__lte=end,
        ).order_by("date")
    )
    daily_series = _daily_series_from_snapshots(metrics, start, end)

    status_counts = _entry_status_counts([queue.pk])
    total_joins = sum(m.joins for m in metrics)
    total_completed = sum(m.completed for m in metrics)
    days_span = max(len(metrics), 1)
    throughput_per_day = round(total_completed / days_span, 2)

    day_start, day_end = _day_bounds(start)
    _, range_end = _day_bounds(end)
    avg_wait = (
        QueueEntry.objects.filter(
            queue=queue,
            status=QueueEntry.Status.COMPLETED,
            completed_at__isnull=False,
            completed_at__gte=day_start,
            completed_at__lte=range_end,
        )
        .annotate(
            wait=ExpressionWrapper(
                F("completed_at") - F("joined_at"),
                output_field=DurationField(),
            )
        )
        .aggregate(avg=Avg("wait"))["avg"]
    )
    avg_wait_seconds = round(avg_wait.total_seconds(), 2) if avg_wait else 0.0

    return {
        "queue_id": queue.id,
        "public_id": str(queue.public_id),
        "name": queue.name,
        "organization_id": queue.organization_id,
        "days": days,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "total_entries": total_joins,
        "waiting_count": status_counts["waiting"],
        "called_count": status_counts["called"],
        "completed_count": status_counts["completed"],
        "throughput_per_day": throughput_per_day,
        "avg_wait_seconds": avg_wait_seconds,
        "daily_series": daily_series,
    }


def get_user_report() -> dict[str, Any]:
    by_role_qs = User.objects.values("role").annotate(count=Count("id"))
    by_role = {row["role"]: row["count"] for row in by_role_qs}

    signups = (
        User.objects.annotate(day=TruncDate("date_joined"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    signups_by_day = [
        {"date": row["day"].isoformat() if row["day"] else None, "count": row["count"]}
        for row in signups
        if row["day"] is not None
    ]

    return {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "by_role": {
            "USER": by_role.get(User.Role.USER, 0),
            "ORGANIZATION": by_role.get(User.Role.ORGANIZATION, 0),
            "ADMIN": by_role.get(User.Role.ADMIN, 0),
        },
        "signups_by_day": signups_by_day,
    }
