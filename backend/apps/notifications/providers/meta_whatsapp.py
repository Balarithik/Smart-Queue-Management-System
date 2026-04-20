import requests
from django.conf import settings


class MetaWhatsAppClient:
    def __init__(self):
        self.base_url = (
            f"https://graph.facebook.com/{settings.META_WHATSAPP_API_VERSION}/{settings.META_WHATSAPP_PHONE_NUMBER_ID}/messages"
        )
        self.headers = {
            "Authorization": f"Bearer {settings.META_WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    def send_template(self, to_number: str, template_name: str, variables: list[str]):
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en_US"},
                "components": [{"type": "body", "parameters": [{"type": "text", "text": v} for v in variables]}],
            },
        }
        return requests.post(self.base_url, headers=self.headers, json=payload, timeout=10)
