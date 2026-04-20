from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from apps.organizations.models import Organization
from apps.queues.models import QueueEntry, Service, Ticket
from .tasks import send_queue_whatsapp_notification

User = get_user_model()


class WhatsAppTaskTests(TestCase):
    def setUp(self):
        admin = User.objects.create_user(username="admin", password="Password123!", role="org_admin", phone_number="15551001")
        user = User.objects.create_user(username="user", password="Password123!", role="user", phone_number="15551002")
        org = Organization.objects.create(name="Org A", slug="org-a", admin=admin)
        service = Service.objects.create(organization=org, name="Service A", code="svc")
        self.entry = QueueEntry.objects.create(service=service, user=user, position=1, estimated_wait_minutes=5)
        Ticket.objects.create(queue_entry=self.entry, token="SVC-0001")

    @patch("apps.notifications.providers.meta_whatsapp.requests.post")
    def test_whatsapp_task(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"messages": [{"id": "wamid.1"}]}
        mock_post.return_value.raise_for_status.return_value = None
        result = send_queue_whatsapp_notification(str(self.entry.id), "join_confirmation")
        self.assertIn("messages", result)
