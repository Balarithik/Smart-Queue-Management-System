"""Transactional queue operations."""

from __future__ import annotations

from django.db import transaction

from queues.models import Queue, QueueEntry


def join_queue(public_id) -> dict:
    """
    Issue the next token and create a WAITING entry.
    Locks the Queue row with select_for_update.
    """
    with transaction.atomic():
        queue = Queue.objects.select_for_update().get(public_id=public_id)
        if not queue.is_active:
            raise ValueError("This queue is not accepting new entries.")
        new_token = queue.last_token_issued + 1
        queue.last_token_issued = new_token
        queue.save(update_fields=["last_token_issued"])
        entry = QueueEntry.objects.create(
            queue=queue,
            token=new_token,
            status=QueueEntry.Status.WAITING,
        )
        ahead = QueueEntry.objects.filter(
            queue=queue,
            status=QueueEntry.Status.WAITING,
            token__lt=new_token,
        ).count()

        from notifications.hooks import notify_user_joined_queue

        def _after_join() -> None:
            notify_user_joined_queue(queue, entry, waiting_ahead=ahead)
            from queues.realtime import publish_queue_update

            publish_queue_update(queue, entry)

        transaction.on_commit(_after_join)

        return {
            "token": new_token,
            "waiting_ahead": ahead,
            "queue_name": queue.name,
            "status": QueueEntry.Status.WAITING,
            "public_id": str(queue.public_id),
        }
