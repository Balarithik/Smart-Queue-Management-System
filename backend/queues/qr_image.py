"""PNG QR codes: join URL, files under MEDIA_ROOT/qr/, and API helpers."""

from __future__ import annotations

import base64
import io
from pathlib import Path

import qrcode
from django.conf import settings


def join_url_for_queue(public_id) -> str:
    base = getattr(settings, "FRONTEND_ORIGIN", "http://127.0.0.1:5173").rstrip("/")
    return f"{base}/join/{public_id}"


def _render_qr_png_bytes(url: str) -> bytes:
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def ensure_queue_qr_file(public_id) -> str:
    """
    Ensure PNG exists at MEDIA_ROOT/qr/{public_id}.png.
    Returns path relative to MEDIA_ROOT with forward slashes, e.g. qr/<uuid>.png
    """
    safe_id = str(public_id)
    rel = f"qr/{safe_id}.png"
    dest = Path(settings.MEDIA_ROOT) / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return rel
    data = _render_qr_png_bytes(join_url_for_queue(public_id))
    dest.write_bytes(data)
    return rel


def qr_png_base64(public_id) -> str:
    ensure_queue_qr_file(public_id)
    path = Path(settings.MEDIA_ROOT) / "qr" / f"{public_id}.png"
    return base64.b64encode(path.read_bytes()).decode("ascii")


def qr_image_absolute_url(public_id, request) -> str | None:
    """Absolute URL to the saved QR image (requires request for host)."""
    rel = ensure_queue_qr_file(public_id)
    media_url = settings.MEDIA_URL
    if not media_url.startswith("/"):
        media_url = "/" + media_url
    if not media_url.endswith("/"):
        media_url += "/"
    path = f"{media_url}{rel}"
    if request is not None:
        return request.build_absolute_uri(path)
    return path
