import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from organizations.models import Organization
from queues.models import Queue


def _png_file(name: str = "logo.png", size: tuple[int, int] = (32, 32)) -> SimpleUploadedFile:
    buf = io.BytesIO()
    Image.new("RGB", size, color="red").save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")


class QueueImageUploadTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="imgowner",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.org = Organization.objects.create(
            owner=self.owner,
            name="Image Clinic",
            slug="image-clinic",
        )

    def test_create_queue_with_image_returns_image_url(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("queue-create")
        response = self.client.post(
            url,
            {"name": "Branded Desk", "slug": "branded-desk", "image": _png_file()},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("image_url", response.data)
        self.assertIsNotNone(response.data["image_url"])
        queue = Queue.objects.get(public_id=response.data["public_id"])
        self.assertTrue(queue.image)

    def test_reject_invalid_image_type(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("queue-create")
        bad = SimpleUploadedFile("x.gif", b"GIF89a", content_type="image/gif")
        response = self.client.post(
            url,
            {"name": "Bad", "image": bad},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_without_image_still_works(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("queue-create")
        response = self.client.post(
            url,
            {"name": "Plain Desk"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data.get("image_url"))
