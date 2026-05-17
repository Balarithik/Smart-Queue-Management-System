from django.utils.text import slugify
from rest_framework import serializers

from organizations.models import Organization
from queues.models import Queue


class QueueSerializer(serializers.ModelSerializer):
    join_url = serializers.SerializerMethodField()
    qr_image_url = serializers.SerializerMethodField()
    qr_png_base64 = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Queue
        fields = (
            "id",
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
        read_only_fields = fields

    def get_join_url(self, obj):
        from queues.qr_image import join_url_for_queue

        return join_url_for_queue(obj.public_id)

    def get_qr_image_url(self, obj):
        from queues.qr_image import qr_image_absolute_url

        return qr_image_absolute_url(obj.public_id, self.context.get("request"))

    def get_qr_png_base64(self, obj):
        from queues.qr_image import qr_png_base64

        return qr_png_base64(obj.public_id)

    def get_image_url(self, obj):
        from queues.media_urls import queue_image_absolute_url

        return queue_image_absolute_url(obj, self.context.get("request"))


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "owner_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class OrganizationCreateSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False, allow_blank=True, max_length=255)

    class Meta:
        model = Organization
        fields = ("name", "slug", "description")

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            if Organization.objects.filter(owner=user).exists():
                raise serializers.ValidationError(
                    {"detail": "You already have an organization."}
                )
        return attrs

    def validate_slug(self, value):
        value = (value or "").strip()
        if not value:
            return ""
        if Organization.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                "An organization with this slug already exists."
            )
        return value

    def create(self, validated_data):
        request = self.context["request"]
        slug_input = validated_data.pop("slug", "").strip()
        name = validated_data["name"]
        if slug_input:
            slug = slug_input
        else:
            slug = slugify(name) or "organization"
        base = slug
        n = 1
        while Organization.objects.filter(slug=slug).exists():
            slug = f"{base}-{n}"
            n += 1
        return Organization.objects.create(
            owner=request.user,
            slug=slug,
            **validated_data,
        )
