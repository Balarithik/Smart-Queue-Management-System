from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationFlowTests(APITestCase):
    def test_register_user_defaults_role_and_returns_tokens(self):
        url = reverse("accounts-register")
        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "securepass1",
            "password_confirm": "securepass1",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["username"], "alice")
        self.assertEqual(response.data["role"], User.Role.USER)

        user = User.objects.get(username="alice")
        self.assertEqual(user.role, User.Role.USER)
        self.assertTrue(user.check_password("securepass1"))

    def test_register_organization_role(self):
        url = reverse("accounts-register")
        payload = {
            "username": "org1",
            "email": "org@example.com",
            "password": "securepass1",
            "password_confirm": "securepass1",
            "role": User.Role.ORGANIZATION,
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], User.Role.ORGANIZATION)

    def test_register_rejects_admin_role(self):
        url = reverse("accounts-register")
        payload = {
            "username": "badadmin",
            "email": "a@example.com",
            "password": "securepass1",
            "password_confirm": "securepass1",
            "role": User.Role.ADMIN,
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_tokens_with_role_claim(self):
        User.objects.create_user(
            username="bob",
            password="securepass1",
            role=User.Role.USER,
        )
        url = reverse("accounts-token")
        response = self.client.post(
            url,
            {"username": "bob", "password": "securepass1"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_returns_new_access_token(self):
        user = User.objects.create_user(
            username="carol",
            password="securepass1",
            role=User.Role.USER,
        )
        login_url = reverse("accounts-token")
        login = self.client.post(
            login_url,
            {"username": "carol", "password": "securepass1"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        refresh_token = login.data["refresh"]

        refresh_url = reverse("accounts-token-refresh")
        refreshed = self.client.post(
            refresh_url,
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(refreshed.status_code, status.HTTP_200_OK)
        self.assertIn("access", refreshed.data)

    def test_me_requires_authentication(self):
        url = reverse("accounts-me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_profile_when_authenticated(self):
        user = User.objects.create_user(
            username="dana",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.client.force_authenticate(user=user)
        url = reverse("accounts-me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "dana")
        self.assertEqual(response.data["role"], User.Role.ORGANIZATION)


class RolePermissionTests(APITestCase):
    def test_admin_ping_requires_admin_role(self):
        admin = User.objects.create_user(
            username="admin",
            password="securepass1",
            role=User.Role.ADMIN,
        )
        user = User.objects.create_user(
            username="plain",
            password="securepass1",
            role=User.Role.USER,
        )

        url = reverse("accounts-admin-ping")
        self.client.force_authenticate(user=user)
        denied = self.client.get(url)
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=admin)
        ok = self.client.get(url)
        self.assertEqual(ok.status_code, status.HTTP_200_OK)
        self.assertEqual(ok.data["detail"], "admin")
