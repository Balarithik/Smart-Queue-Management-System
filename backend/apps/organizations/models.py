from django.conf import settings
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="admin_orgs")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["slug"])]


class AgentCounter(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="counters")
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="counters")
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "name")
