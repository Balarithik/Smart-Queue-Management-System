from django.utils.text import slugify
from rest_framework import serializers

from accounts.models import User
from organizations.models import Organization
from queues.models import Queue, QueueEntry


class QueueEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = QueueEntry
        fields = ("id", "token", "status", "joined_at")
        read_only_fields = fields


class QueueStaffSerializer(serializers.ModelSerializer):
    """Serializer for staff-facing queue detail."""

    join_url = serializers.SerializerMethodField()
    qr_image_url = serializers.SerializerMethodField()
    qr_png_base64 = serializers.SerializerMethodField()

    class Meta:
        model = Queue
        fields = (
            "id",
            "organization_id",
            "public_id",
            "name",
            "slug",
            "is_active",
            "last_token_issued",
            "created_at",
            "join_url",
            "qr_image_url",
            "qr_png_base64",
        )
        read_only_fields = (
            "id",
            "organization_id",
            "public_id",
            "name",
            "slug",
            "is_active",
            "last_token_issued",
            "created_at",
            "join_url",
            "qr_image_url",
            "qr_png_base64",
        )

    def get_join_url(self, obj: Queue) -> str:
        from queues.qr_image import join_url_for_queue

        return join_url_for_queue(obj.public_id)

    def get_qr_image_url(self, obj: Queue) -> str | None:
        from queues.qr_image import qr_image_absolute_url

        return qr_image_absolute_url(obj.public_id, self.context.get("request"))

    def get_qr_png_base64(self, obj: Queue) -> str:
        from queues.qr_image import qr_png_base64

        return qr_png_base64(obj.public_id)


class QueueCreateSerializer(serializers.ModelSerializer):
    organization_id = serializers.IntegerField(required=False, write_only=True)
    slug = serializers.SlugField(required=False, allow_blank=True, max_length=255)

    class Meta:
        model = Queue
        fields = ("name", "slug", "organization_id")

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        role = getattr(user, "role", User.Role.USER)
        org_id = attrs.pop("organization_id", None)

        if role == User.Role.ADMIN:
            if org_id is None:
                raise serializers.ValidationError(
                    {"organization_id": "This field is required for administrator users."}
                )
            org = Organization.objects.filter(pk=org_id).first()
            if org is None:
                raise serializers.ValidationError(
                    {"organization_id": "Organization not found."}
                )
        else:
            try:
                org = user.organization
            except Organization.DoesNotExist:
                raise serializers.ValidationError(
                    {"detail": "You must belong to an organization to create a queue."}
                )

        attrs["_organization"] = org
        return attrs

    def validate_slug(self, value):
        return (value or "").strip()

    def create(self, validated_data):
        org = validated_data.pop("_organization")
        name = validated_data["name"]
        slug_raw = validated_data.pop("slug", "").strip()
        if slug_raw:
            slug = slugify(slug_raw) or slugify(name) or "queue"
        else:
            slug = slugify(name) or "queue"
        base = slug
        n = 1
        while Queue.objects.filter(organization=org, slug=slug).exists():
            slug = f"{base}-{n}"
            n += 1
        return Queue.objects.create(organization=org, name=name, slug=slug)


class QueuePublicSerializer(serializers.ModelSerializer):
    """Minimal queue info for anonymous clients."""

    class Meta:
        model = Queue
        fields = ("name", "is_active", "public_id")


class QueueStatusSnapshotSerializer(serializers.Serializer):
    """Validated polling / realtime snapshot payload."""

    public_id = serializers.UUIDField()
    queue_name = serializers.CharField()
    queue_status = serializers.ChoiceField(choices=["OPEN", "CLOSED"])
    is_active = serializers.BooleanField()
    current_token = serializers.IntegerField(allow_null=True)
    waiting_count = serializers.IntegerField()
    token = serializers.IntegerField()
    status = serializers.ChoiceField(choices=QueueEntry.Status.choices)
    position = serializers.IntegerField()
    waiting_ahead = serializers.IntegerField()
    eta_seconds = serializers.IntegerField(allow_null=True)
    updated_at = serializers.DateTimeField()
