"""Model signals that translate persistence changes into notification hooks."""

from __future__ import annotations

from django.db import transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver

from notifications.hooks import notify_queue_closed
from queues.models import Queue


@receiver(pre_save, sender=Queue)
def queue_closing_notify(sender, instance, **kwargs):
    """
    When ``is_active`` transitions True -> False, schedule ``notify_queue_closed``
    after the surrounding transaction commits.
    """
    if instance.pk is None:
        return

    try:
        previous = Queue.objects.get(pk=instance.pk)
    except Queue.DoesNotExist:
        return

    if previous.is_active and not instance.is_active:
        pk = instance.pk

        def _on_commit():
            closed = Queue.objects.get(pk=pk)
            notify_queue_closed(closed)

        transaction.on_commit(_on_commit)
