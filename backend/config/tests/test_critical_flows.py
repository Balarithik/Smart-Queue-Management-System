"""
End-to-end API flows for production-critical paths:
register/login, queue join, call next.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from queues.models import QueueEntry


class CriticalFlowTests(APITestCase):
    """Single journey: org signup → queue → join → advance."""

    def test_full_queue_operator_journey(self):
        register_url = reverse("accounts-register")
        reg = self.client.post(
            register_url,
            {
                "username": "floworg",
                "email": "flow@example.com",
                "password": "securepass1",
                "password_confirm": "securepass1",
                "role": User.Role.ORGANIZATION,
            },
            format="json",
        )
        self.assertEqual(reg.status_code, status.HTTP_201_CREATED)
        access = reg.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        org_res = self.client.post(
            reverse("organization-create"),
            {"name": "Flow Clinic", "slug": "flow-clinic"},
            format="json",
        )
        self.assertEqual(org_res.status_code, status.HTTP_201_CREATED)

        queue_res = self.client.post(
            reverse("queue-create"),
            {"name": "Front Desk", "slug": "front-desk"},
            format="json",
        )
        self.assertEqual(queue_res.status_code, status.HTTP_201_CREATED)
        public_id = queue_res.data["public_id"]

        self.client.credentials()
        join_url = reverse("queue-join", kwargs={"public_id": public_id})
        j1 = self.client.post(join_url, {}, format="json")
        j2 = self.client.post(join_url, {}, format="json")
        self.assertEqual(j1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(j2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(j1.data["token"], 1)
        self.assertEqual(j2.data["waiting_ahead"], 1)

        status_url = reverse("queue-status", kwargs={"public_id": public_id})
        waiting = self.client.get(status_url, {"token": 2})
        self.assertEqual(waiting.status_code, status.HTTP_200_OK)
        self.assertEqual(waiting.data["position"], 2)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        next_url = reverse("queue-next", kwargs={"public_id": public_id})
        n1 = self.client.post(next_url, {}, format="json")
        self.assertEqual(n1.status_code, status.HTTP_200_OK)
        self.assertEqual(n1.data["called_token"], 1)

        entry = QueueEntry.objects.get(queue__public_id=public_id, token=1)
        self.assertEqual(entry.status, QueueEntry.Status.CALLED)

    def test_auth_login_refresh_me(self):
        User.objects.create_user(
            username="flowuser",
            password="securepass1",
            role=User.Role.USER,
        )
        login = self.client.post(
            reverse("accounts-token"),
            {"username": "flowuser", "password": "securepass1"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        refresh = self.client.post(
            reverse("accounts-token-refresh"),
            {"refresh": login.data["refresh"]},
            format="json",
        )
        self.assertEqual(refresh.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.data['access']}")
        me = self.client.get(reverse("accounts-me"))
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["username"], "flowuser")
