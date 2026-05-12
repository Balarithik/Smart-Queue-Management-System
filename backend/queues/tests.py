from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from organizations.models import Organization
from queues.models import Queue, QueueEntry


class QueueFlowTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="qowner",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.org = Organization.objects.create(
            owner=self.owner,
            name="Clinic",
            slug="clinic",
        )
        self.queue = Queue.objects.create(
            organization=self.org,
            name="Desk",
            slug="desk",
        )

    def test_create_queue_returns_public_id_and_qr(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("queue-create")
        response = self.client.post(
            url,
            {"name": "New Desk", "slug": "new-desk"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("public_id", response.data)
        self.assertIn("qr_png_base64", response.data)
        self.assertIn("join_url", response.data)
        q = Queue.objects.get(public_id=response.data["public_id"])
        self.assertEqual(q.organization_id, self.org.id)

    def test_join_increments_token_and_returns_position(self):
        url = reverse("queue-join", kwargs={"public_id": str(self.queue.public_id)})
        r1 = self.client.post(url, {}, format="json")
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r1.data["token"], 1)
        self.assertEqual(r1.data["waiting_ahead"], 0)

        r2 = self.client.post(url, {}, format="json")
        self.assertEqual(r2.data["token"], 2)
        self.assertEqual(r2.data["waiting_ahead"], 1)

    def test_next_marks_waiting_as_called(self):
        join_url = reverse("queue-join", kwargs={"public_id": str(self.queue.public_id)})
        self.client.post(join_url, {}, format="json")
        self.client.post(join_url, {}, format="json")

        self.client.force_authenticate(user=self.owner)
        next_url = reverse("queue-next", kwargs={"public_id": str(self.queue.public_id)})
        r = self.client.post(next_url, {}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["called_token"], 1)
        self.assertEqual(r.data["remaining_waiting"], 1)

        e = QueueEntry.objects.get(queue=self.queue, token=1)
        self.assertEqual(e.status, QueueEntry.Status.CALLED)

    def test_next_empty_queue_returns_null_token(self):
        self.client.force_authenticate(user=self.owner)
        next_url = reverse("queue-next", kwargs={"public_id": str(self.queue.public_id)})
        r = self.client.post(next_url, {}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIsNone(r.data["called_token"])

    def test_join_inactive_queue_returns_400(self):
        self.queue.is_active = False
        self.queue.save(update_fields=["is_active"])
        url = reverse("queue-join", kwargs={"public_id": str(self.queue.public_id)})
        r = self.client.post(url, {}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_status_endpoint_requires_token_query(self):
        url = reverse("queue-status", kwargs={"public_id": str(self.queue.public_id)})
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
