"""WSGI entry point for containerized and managed deployments."""

from . import create_app

app = create_app()
