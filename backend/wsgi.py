"""WSGI entry point for production deployment with Gunicorn."""

from app import create_app

app = create_app()
