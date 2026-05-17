"""Gunicorn configuration for production (see deploy/nginx and README)."""

import multiprocessing
import os

bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")
workers = int(os.environ.get("GUNICORN_WORKERS", max(2, multiprocessing.cpu_count())))
threads = int(os.environ.get("GUNICORN_THREADS", "1"))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "60"))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
capture_output = True

wsgi_app = "config.wsgi:application"
