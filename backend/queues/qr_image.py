"""PNG QR codes as base64 for API responses."""

from __future__ import annotations

import base64
import io

import qrcode
from django.conf import settings


def join_url_for_queue(public_id) -> str:
    base = getattr(settings, "FRONTEND_ORIGIN", "http://127.0.0.1:5173").rstrip("/")
    return f"{base}/join/{public_id}"


def qr_png_base64(url: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")
