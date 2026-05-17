"""Production-oriented settings; rely on environment variables."""

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

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)  # noqa: F405
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT

if SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # noqa: F405
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=False)  # noqa: F405

if SECRET_KEY.startswith("django-insecure"):  # noqa: F405
    raise ImproperlyConfigured("Set a strong SECRET_KEY in production.")

# User-generated files (QR images) are served by Nginx in production, not Django.
# See deploy/nginx/sqms.conf and docker-compose.prod.yml.
