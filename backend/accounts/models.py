from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Application user with a coarse role used for authorization."""

    class Role(models.TextChoices):
        USER = "USER", "User"
        ORGANIZATION = "ORGANIZATION", "Organization"
        ADMIN = "ADMIN", "Administrator"

    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.USER,
        db_index=True,
    )

    def __str__(self) -> str:
        return self.username
