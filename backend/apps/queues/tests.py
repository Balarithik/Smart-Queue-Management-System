from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from apps.organizations.models import Organization
from .models import QueueEntry, Service

User = get_user_model()


class QueueModelTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="Password123!", role="org_admin", phone_number="15550101"
        )
        self.user = User.objects.create_user(username="u1", password="Password123!", role="user", phone_number="15550102")
        self.org = Organization.objects.create(name="Org", slug="org", admin=self.admin)
        self.service = Service.objects.create(organization=self.org, name="General", code="gen")

    def test_join_queue_creates_entry(self):
        entry = QueueEntry.objects.create(service=self.service, user=self.user, position=1, estimated_wait_minutes=5)
        self.assertEqual(entry.status, "waiting")


class QueueApiFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="user", password="Password123!", role="user", phone_number="15550201")
        self.admin = User.objects.create_user(
            username="admin2", password="Password123!", role="org_admin", phone_number="15550202"
        )
        self.org = Organization.objects.create(name="Org 2", slug="org-2", admin=self.admin)
        self.service = Service.objects.create(organization=self.org, name="Lab", code="lab")

    def test_join_queue_endpoint(self):
        self.client.force_authenticate(self.user)
        response = self.client.post("/api/v1/queues/entries/join/", {"service": self.service.id}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "waiting")
