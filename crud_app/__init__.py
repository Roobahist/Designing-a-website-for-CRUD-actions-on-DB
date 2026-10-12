"""Application factory for the employee training database CRUD demo."""

from __future__ import annotations

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .config import Settings
from .repository import TableRepository
from .views import register_routes


def create_app(settings: Settings | None = None, engine: Engine | None = None) -> Flask:
    """Wire configuration, database infrastructure, and web routes together."""
    settings = settings if settings is not None else Settings.from_env()
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=settings.secret_key,
        MAX_CONTENT_LENGTH=128 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=settings.cookie_secure,
    )
    database_engine = engine if engine is not None else create_engine(
        settings.database_url, pool_pre_ping=True
    )
    repository = TableRepository(database_engine, page_size=settings.page_size)
    app.extensions["table_repository"] = repository
    register_routes(app, repository, settings)
    return app
