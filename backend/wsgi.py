"""WSGI entrypoint for Gunicorn on Render (`gunicorn backend.wsgi:application`)."""

import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from config.wsgi import application

__all__ = ["application"]
