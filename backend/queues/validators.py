"""Validators for queue image uploads."""

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_queue_image(file) -> None:
    """Allow JPEG/PNG only, within QUEUE_IMAGE_MAX_BYTES."""
    if file is None:
        return

    max_bytes = getattr(settings, "QUEUE_IMAGE_MAX_BYTES", 2_097_152)
    allowed = getattr(
        settings,
        "QUEUE_IMAGE_ALLOWED_CONTENT_TYPES",
        ["image/jpeg", "image/png"],
    )

    if file.size > max_bytes:
        raise ValidationError(
            f"Image must be at most {max_bytes // 1024} KB."
        )

    content_type = getattr(file, "content_type", "") or ""
    if content_type and content_type not in allowed:
        raise ValidationError("Only JPEG and PNG images are allowed.")

    name = (getattr(file, "name", "") or "").lower()
    if name and not (name.endswith(".jpg") or name.endswith(".jpeg") or name.endswith(".png")):
        raise ValidationError("File extension must be .jpg, .jpeg, or .png.")
