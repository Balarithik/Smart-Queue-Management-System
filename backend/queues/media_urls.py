"""Absolute URLs for queue media assets."""

from __future__ import annotations

from django.conf import settings


def queue_image_absolute_url(queue, request) -> str | None:
    """Absolute URL for an uploaded queue image, or None if no image."""
    if not queue.image:
        return None
    try:
        url = queue.image.url
    except ValueError:
        return None
    if not url.startswith("/"):
        url = "/" + url
    if request is not None:
        return request.build_absolute_uri(url)
    return url
