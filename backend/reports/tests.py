from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from organizations.models import Organization
from queues.models import Queue, QueueEntry
from reports.models import DailyQueueMetric
from reports.services import get_org_report, refresh_daily_snapshots_for_queue


class ReportsAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="reportowner",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.other = User.objects.create_user(
            username="reportother",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.admin = User.objects.create_user(
            username="reportadmin",
            password="securepass1",
            role=User.Role.ADMIN,
        )
        self.plain = User.objects.create_user(
            username="reportuser",
            password="securepass1",
            role=User.Role.USER,
        )
        self.org = Organization.objects.create(
            owner=self.owner,
            name="Report Clinic",
            slug="report-clinic",
        )
        self.queue = Queue.objects.create(
            organization=self.org,
            name="Desk",
            slug="desk",
        )

    def _join_and_next(self, count: int = 1) -> None:
        join_url = reverse("queue-join", kwargs={"public_id": str(self.queue.public_id)})
        next_url = reverse("queue-next", kwargs={"public_id": str(self.queue.public_id)})
        for _ in range(count):
            self.client.post(join_url, {}, format="json")
        self.client.force_authenticate(user=self.owner)
        for _ in range(count):
            self.client.post(next_url, {}, format="json")

    def test_owner_can_read_org_report(self):
        self._join_and_next(2)
        self.client.force_authenticate(user=self.owner)
        url = reverse("report-organization", kwargs={"pk": self.org.pk})
        response = self.client.get(url, {"days": 30})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["organization_id"], self.org.id)
        self.assertEqual(response.data["queue_count"], 1)
        self.assertGreaterEqual(response.data["total_entries"], 2)
        self.assertIn("daily_series", response.data)
        self.assertEqual(len(response.data["queues"]), 1)

    def test_non_owner_denied_org_report(self):
        self.client.force_authenticate(user=self.other)
        url = reverse("report-organization", kwargs={"pk": self.org.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_read_org_report(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("report-organization", kwargs={"pk": self.org.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_queue_report_after_join_and_next(self):
        self._join_and_next(1)
        self.client.force_authenticate(user=self.owner)
        url = reverse("report-queue", kwargs={"public_id": str(self.queue.public_id)})
        response = self.client.get(url, {"days": 7})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["public_id"], str(self.queue.public_id))
        self.assertGreaterEqual(response.data["total_entries"], 1)
        self.assertEqual(response.data["called_count"], 1)
        self.assertIn("daily_series", response.data)

    def test_admin_can_read_user_report(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("report-users")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["total_users"], 4)
        self.assertIn("by_role", response.data)
        self.assertIn("signups_by_day", response.data)

    def test_non_admin_denied_user_report(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("report-users")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_snapshot_upsert_is_idempotent(self):
        QueueEntry.objects.create(queue=self.queue, token=1)
        from reports.services import report_date_range

        start, end = report_date_range(7)
        refresh_daily_snapshots_for_queue(self.queue, start, end)
        count_first = DailyQueueMetric.objects.filter(queue=self.queue).count()
        refresh_daily_snapshots_for_queue(self.queue, start, end)
        count_second = DailyQueueMetric.objects.filter(queue=self.queue).count()
        self.assertEqual(count_first, count_second)
        self.assertEqual(count_first, 7)

    def test_get_org_report_populates_snapshots(self):
        QueueEntry.objects.create(
            queue=self.queue,
            token=10,
            status=QueueEntry.Status.WAITING,
        )
        data = get_org_report(self.org, days=7)
        self.assertEqual(data["waiting_count"], 1)
        self.assertTrue(DailyQueueMetric.objects.filter(queue=self.queue).exists())


class PlatformDashboardAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="platformowner",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.admin = User.objects.create_user(
            username="platformadmin",
            password="securepass1",
            role=User.Role.ADMIN,
        )
        self.org = Organization.objects.create(
            owner=self.owner,
            name="Platform Clinic",
            slug="platform-clinic",
        )
        self.queue = Queue.objects.create(
            organization=self.org,
            name="Front Desk",
            slug="front-desk",
            is_active=True,
        )
        QueueEntry.objects.create(
            queue=self.queue,
            token=1,
            status=QueueEntry.Status.WAITING,
        )

    def test_admin_can_read_platform_dashboard(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("report-platform")
        response = self.client.get(url, {"days": 7})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["days"], 7)
        self.assertEqual(len(response.data["daily_series"]), 7)
        self.assertGreaterEqual(response.data["users"]["total_users"], 2)
        self.assertEqual(response.data["organizations"]["total"], 1)
        self.assertEqual(response.data["queues"]["total"], 1)
        self.assertEqual(response.data["queues"]["active"], 1)
        self.assertEqual(response.data["queues"]["waiting_count"], 1)

    def test_non_admin_denied_platform_dashboard(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("report-platform")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
