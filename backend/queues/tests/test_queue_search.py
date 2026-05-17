from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from organizations.models import Organization
from queues.models import Queue, QueueEntry


class QueueSearchTests(APITestCase):
    def setUp(self):
        owner = User.objects.create_user(
            username="searchowner",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.org_a = Organization.objects.create(
            owner=owner,
            name="Alpha Medical",
            slug="alpha-medical",
        )
        self.queue_a = Queue.objects.create(
            organization=self.org_a,
            name="Front Desk",
            slug="front-desk",
        )
        owner_b = User.objects.create_user(
            username="searchowner2",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.org_b = Organization.objects.create(
            owner=owner_b,
            name="Beta Clinic",
            slug="beta-clinic",
        )
        self.queue_b = Queue.objects.create(
            organization=self.org_b,
            name="Pharmacy Line",
            slug="pharmacy-line",
        )
        QueueEntry.objects.create(
            queue=self.queue_a,
            token=1,
            status=QueueEntry.Status.WAITING,
        )

    def test_search_by_queue_name(self):
        url = reverse("queue-search")
        response = self.client.get(url, {"q": "pharmacy"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [row["name"] for row in response.data["results"]]
        self.assertEqual(names, ["Pharmacy Line"])

    def test_search_by_organization_name(self):
        url = reverse("queue-search")
        response = self.client.get(url, {"q": "alpha"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["organization_name"], "Alpha Medical")

    def test_empty_query_returns_active_queues_paginated(self):
        url = reverse("queue-search")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 2)
        self.assertIn("waiting_count", response.data["results"][0])

    def test_pagination_page_size(self):
        url = reverse("queue-search")
        response = self.client.get(url, {"page_size": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIsNotNone(response.data["next"])
