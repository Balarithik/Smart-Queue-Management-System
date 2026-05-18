"""WSGI entrypoint for Gunicorn on Render (see Procfile)."""

from config.wsgi import application

__all__ = ["application"]
