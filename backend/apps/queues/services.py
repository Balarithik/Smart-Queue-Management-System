from django.db import transaction
from django.utils import timezone
from apps.notifications.tasks import send_queue_whatsapp_notification
from .models import QueueEntry, Service, Ticket


def publish_queue_event(channel_layer, group_name: str, event_type: str, payload: dict):
    from asgiref.sync import async_to_sync

    async_to_sync(channel_layer.group_send)(
        group_name,
        {"type": "queue.message", "event_type": event_type, "payload": payload, "timestamp": timezone.now().isoformat()},
    )


@transaction.atomic
def join_queue(service: Service, user):
    existing = QueueEntry.objects.filter(
        service=service, user=user, status__in=[QueueEntry.Status.WAITING, QueueEntry.Status.CALLED, QueueEntry.Status.SERVING]
    ).first()
    if existing:
        return existing

    waiting_count = QueueEntry.objects.filter(service=service, status=QueueEntry.Status.WAITING).count()
    entry = QueueEntry.objects.create(
        service=service,
        user=user,
        position=waiting_count + 1,
        estimated_wait_minutes=(waiting_count + 1) * service.average_service_minutes,
    )
    Ticket.objects.create(queue_entry=entry, token=f"{service.code.upper()}-{entry.id:04d}")
    send_queue_whatsapp_notification.delay(str(entry.id), "join_confirmation")
    return entry
