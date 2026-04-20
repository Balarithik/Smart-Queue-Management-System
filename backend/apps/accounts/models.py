from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", "User"
        ORG_ADMIN = "org_admin", "Organization Admin"
        AGENT = "agent", "Agent"

    phone_number = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER, db_index=True)
    whatsapp_opt_in = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["role", "is_active"])]
