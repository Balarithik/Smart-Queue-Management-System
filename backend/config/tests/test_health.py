from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class HealthEndpointTests(TestCase):
    def test_health_returns_ok_with_database(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["checks"]["database"], "ok")
        self.assertEqual(response.json()["service"], "smart-queue-api")

    @patch("config.views.connection")
    def test_health_returns_503_when_database_unavailable(self, mock_connection):
        mock_connection.ensure_connection.side_effect = Exception("database unavailable")
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "unavailable")
        self.assertEqual(response.json()["checks"]["database"], "unavailable")
