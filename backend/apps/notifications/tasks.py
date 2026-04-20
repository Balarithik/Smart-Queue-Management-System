from celery import shared_task
from apps.queues.models import QueueEntry
from .providers.meta_whatsapp import MetaWhatsAppClient

TEMPLATES = {
    "join_confirmation": ("queue_join_confirmation", ["{ticket}", "{position}", "{eta}"]),
    "position_update": ("queue_position_update", ["{ticket}", "{position}", "{eta}"]),
    "counter_call": ("queue_counter_call", ["{ticket}", "{counter}", "{eta}"]),
}


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_queue_whatsapp_notification(self, queue_entry_id: str, event_name: str):
    entry = QueueEntry.objects.select_related("user", "ticket").get(pk=queue_entry_id)
    if not entry.user.whatsapp_opt_in:
        return {"status": "skipped", "reason": "opt_out"}
    template_name, template_vars = TEMPLATES[event_name]
    context = {
        "ticket": entry.ticket.token,
        "position": str(entry.position),
        "eta": str(entry.estimated_wait_minutes),
        "counter": entry.ticket.counter.name if entry.ticket.counter else "TBD",
    }
    variables = [v.format(**context) for v in template_vars]
    response = MetaWhatsAppClient().send_template(entry.user.phone_number, template_name, variables)
    response.raise_for_status()
    return response.json()
