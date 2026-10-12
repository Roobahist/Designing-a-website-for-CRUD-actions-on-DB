"""Optional MySQL 8 integration check for the actual project schema."""

from __future__ import annotations

import base64
import os
import re
from pathlib import Path

import pytest
from sqlalchemy import create_engine

from crud_app import create_app
from crud_app.config import Settings
from crud_app.repository import SUPPORTED_TABLES

DATABASE_URL = os.getenv("TEST_MYSQL_DATABASE_URL")


@pytest.mark.skipif(not DATABASE_URL, reason="MySQL integration URL not configured")
def test_mysql_schema_seed_and_crud():
    """Initialize a disposable MySQL database and exercise actual reflected types."""
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            for filename in ("schema.sql", "demo_seed.sql"):
                sql = (Path(__file__).parents[1] / "database" / filename).read_text()
                for statement in sql.split(";"):
                    if statement.strip():
                        connection.exec_driver_sql(statement)

        settings = Settings(
            database_url=DATABASE_URL,
            admin_password="mysql-test-password",
            secret_key="mysql-testing-secret-with-at-least-32-chars",
        )
        app = create_app(settings=settings, engine=engine)
        app.testing = True
        repo = app.extensions["table_repository"]
        assert set(repo.table_names) == set(SUPPORTED_TABLES)
        assert len(repo.list_records("employee")[0]) == 7
        assert len(repo.list_records("course_class_days")[0]) == 5
        client = app.test_client()
        auth = base64.b64encode(b"admin:mysql-test-password").decode("ascii")
        headers = {"Authorization": "Basic " + auth}

        # The original courses include MySQL DATE and TIME(6) columns.
        page = client.get("/tables/course", headers=headers)
        assert page.status_code == 200
        assert b"Databases" in page.data
        form = client.get("/tables/role/new", headers=headers)
        assert form.status_code == 200
        token = re.search(rb'name="csrf_token" value="([^"]+)"', form.data)
        assert token is not None
        created = client.post(
            "/tables/role/create", headers=headers,
            data={
                "role_id": "100", "role_name": "Integration Tester", "role_desc": "",
                "csrf_token": token.group(1).decode(),
            },
        )
        assert created.status_code == 303
        role = next(row for row in repo.list_records("role")[0] if row["role_id"] == 100)
        key = repo.record_key("role", role)
        assert repo.get_record("role", key)["role_name"].strip() == "Integration Tester"
        deleted = client.post(
            f"/tables/role/delete/{key}", headers=headers,
            data={"csrf_token": token.group(1).decode()},
        )
        assert deleted.status_code == 303
    finally:
        engine.dispose()
