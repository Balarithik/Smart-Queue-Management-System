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
    image_url = serializers.SerializerMethodField()

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
            "image_url",
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
            "image_url",
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

    def get_image_url(self, obj: Queue) -> str | None:
        from queues.media_urls import queue_image_absolute_url

        return queue_image_absolute_url(obj, self.context.get("request"))


class QueueCreateSerializer(serializers.ModelSerializer):
    organization_id = serializers.IntegerField(required=False, write_only=True)
    slug = serializers.SlugField(required=False, allow_blank=True, max_length=255)
    image = serializers.ImageField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Queue
        fields = ("name", "slug", "organization_id", "image")

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

    def validate_image(self, value):
        if value is not None:
            from django.core.exceptions import ValidationError as DjangoValidationError

            from queues.validators import validate_queue_image

            try:
                validate_queue_image(value)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def create(self, validated_data):
        org = validated_data.pop("_organization")
        image = validated_data.pop("image", None)
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
        queue = Queue.objects.create(organization=org, name=name, slug=slug)
        if image:
            queue.image = image
            queue.save(update_fields=["image"])
        return queue


class QueuePublicSerializer(serializers.ModelSerializer):
    """Minimal queue info for anonymous clients."""

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Queue
        fields = ("name", "is_active", "public_id", "image_url")

    def get_image_url(self, obj: Queue) -> str | None:
        from queues.media_urls import queue_image_absolute_url

        return queue_image_absolute_url(obj, self.context.get("request"))


class QueueSearchSerializer(serializers.ModelSerializer):
    """Public catalog row for search / user dashboard."""

    organization_id = serializers.IntegerField(source="organization.id", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    queue_status = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    waiting_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Queue
        fields = (
            "public_id",
            "name",
            "slug",
            "is_active",
            "queue_status",
            "organization_id",
            "organization_name",
            "image_url",
            "waiting_count",
        )

    def get_queue_status(self, obj: Queue) -> str:
        return "OPEN" if obj.is_active else "CLOSED"

    def get_image_url(self, obj: Queue) -> str | None:
        from queues.media_urls import queue_image_absolute_url

        return queue_image_absolute_url(obj, self.context.get("request"))


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
