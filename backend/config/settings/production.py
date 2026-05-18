"""Production settings for Render and other WSGI hosts."""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

DEBUG = False

if not env("DATABASE_URL", default=None):  # noqa: F405
    raise ImproperlyConfigured("DATABASE_URL must be set in production.")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

_render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if _render_host:
    ALLOWED_HOSTS = list({*ALLOWED_HOSTS, _render_host})  # noqa: F405

# On Render there is no separate Nginx for /media/ — serve uploads from Django when enabled.
SERVE_MEDIA = env.bool("SERVE_MEDIA", default=bool(_render_host))  # noqa: F405

SECURE_SSL_REDIRECT = env.bool(  # noqa: F405
    "SECURE_SSL_REDIRECT",
    default=bool(_render_host),
)
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT

if SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # noqa: F405
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=False)  # noqa: F405

if SECRET_KEY.startswith("django-insecure"):  # noqa: F405
    raise ImproperlyConfigured("Set a strong SECRET_KEY in production.")
