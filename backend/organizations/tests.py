from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from organizations.models import Organization
from queues.models import Queue


class OrganizationCreateAPITests(APITestCase):
    def test_organization_role_can_create_org_once(self):
        user = User.objects.create_user(
            username="orgowner",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.client.force_authenticate(user=user)
        url = reverse("organization-create")
        response = self.client.post(
            url,
            {"name": "Acme Clinic", "description": "Main site"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Acme Clinic")
        self.assertEqual(response.data["slug"], "acme-clinic")
        self.assertTrue(Organization.objects.filter(owner=user).exists())

    def test_second_create_fails_when_org_exists(self):
        user = User.objects.create_user(
            username="orgowner2",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        Organization.objects.create(
            owner=user,
            name="Existing",
            slug="existing",
        )
        self.client.force_authenticate(user=user)
        url = reverse("organization-create")
        response = self.client.post(
            url,
            {"name": "Another"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_role_cannot_create_org(self):
        user = User.objects.create_user(
            username="plainuser",
            password="securepass1",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=user)
        url = reverse("organization-create")
        response = self.client.post(
            url,
            {"name": "Nope"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrganizationAccessAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.other = User.objects.create_user(
            username="intruder",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="securepass1",
            role=User.Role.ADMIN,
        )
        self.org = Organization.objects.create(
            owner=self.owner,
            name="Test Org",
            slug="test-org",
        )
        Queue.objects.create(
            organization=self.org,
            name="Front Desk",
            slug="front-desk",
            is_active=True,
        )
        Queue.objects.create(
            organization=self.org,
            name="Lab",
            slug="lab",
            is_active=False,
        )

    def test_owner_can_list_queues_and_stats(self):
        self.client.force_authenticate(user=self.owner)
        q_url = reverse("organization-queues", kwargs={"pk": self.org.pk})
        s_url = reverse("organization-stats", kwargs={"pk": self.org.pk})

        qr = self.client.get(q_url)
        self.assertEqual(qr.status_code, status.HTTP_200_OK)
        self.assertEqual(len(qr.data), 2)

        sr = self.client.get(s_url)
        self.assertEqual(sr.status_code, status.HTTP_200_OK)
        self.assertEqual(sr.data["queue_count"], 2)
        self.assertEqual(sr.data["active_queue_count"], 1)
        self.assertEqual(sr.data["organization_id"], self.org.id)

    def test_non_owner_non_admin_denied(self):
        self.client.force_authenticate(user=self.other)
        q_url = reverse("organization-queues", kwargs={"pk": self.org.pk})
        qr = self.client.get(q_url)
        self.assertEqual(qr.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_other_org_queues_and_stats(self):
        self.client.force_authenticate(user=self.admin)
        q_url = reverse("organization-queues", kwargs={"pk": self.org.pk})
        s_url = reverse("organization-stats", kwargs={"pk": self.org.pk})
        self.assertEqual(self.client.get(q_url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(s_url).status_code, status.HTTP_200_OK)

    def test_me_returns_org_or_404(self):
        self.client.force_authenticate(user=self.owner)
        me_url = reverse("organization-me")
        r = self.client.get(me_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["slug"], "test-org")

        lone = User.objects.create_user(
            username="noorg",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.client.force_authenticate(user=lone)
        r404 = self.client.get(me_url)
        self.assertEqual(r404.status_code, status.HTTP_404_NOT_FOUND)
