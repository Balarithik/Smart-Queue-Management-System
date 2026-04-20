from rest_framework import serializers
from .models import AgentCounter, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "slug", "admin", "created_at")
        read_only_fields = ("id", "created_at")


class AgentCounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentCounter
        fields = ("id", "organization", "agent", "name", "is_active")
