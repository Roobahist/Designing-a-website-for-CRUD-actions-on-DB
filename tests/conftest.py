"""Shared integration fixtures use a disposable SQLite database."""

import base64
import re

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from crud_app import create_app
from crud_app.config import Settings


@pytest.fixture
def app():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE department ("
            "department_id INTEGER PRIMARY KEY, department_name VARCHAR(60) NOT NULL, "
            "budget REAL NOT NULL)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE course_gives_skill ("
            "course_id INTEGER NOT NULL, skill_id INTEGER NOT NULL, "
            "PRIMARY KEY (course_id, skill_id))"
        )
        connection.exec_driver_sql(
            "INSERT INTO department VALUES (1, 'Engineering', 500.0)"
        )
        connection.exec_driver_sql(
            "INSERT INTO course_gives_skill VALUES (10, 20)"
        )
    settings = Settings(
        database_url="sqlite+pysqlite:///:memory:",
        admin_password="test-password-12345",
        secret_key="test-secret-key-that-is-at-least-32-characters",
        page_size=1,
    )
    app = create_app(settings=settings, engine=engine)
    app.testing = True
    yield app
    engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def headers():
    value = base64.b64encode(b"admin:test-password-12345").decode("ascii")
    return {"Authorization": "Basic " + value}


def csrf_from(response):
    match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
    assert match, "Expected a CSRF token in the HTML form"
    return match.group(1).decode("ascii")
