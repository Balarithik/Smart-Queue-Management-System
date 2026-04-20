from rest_framework import serializers
from .models import QueueEntry, Service, Ticket


class ServiceSerializer(serializers.ModelSerializer):
    qr_join_url = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ("id", "organization", "name", "code", "average_service_minutes", "is_active", "qr_join_url")

    def get_qr_join_url(self, obj):
        return f"/join/{obj.organization.slug}/{obj.code}"


class QueueEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = QueueEntry
        fields = (
            "id",
            "service",
            "user",
            "status",
            "position",
            "estimated_wait_minutes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("position", "estimated_wait_minutes", "created_at", "updated_at")


class TicketSerializer(serializers.ModelSerializer):
    queue_entry = QueueEntrySerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "ticket_id", "token", "counter", "called_at", "served_at", "queue_entry")


class QRJoinSerializer(serializers.Serializer):
    organization_slug = serializers.SlugField()
    service_code = serializers.SlugField()
    phone_number = serializers.CharField(max_length=20)
