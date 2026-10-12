"""HTML administration routes, authentication, and request protection."""

from __future__ import annotations

import hmac
import secrets

from flask import (
    Flask, Response, abort, redirect, render_template, request, session, url_for,
)
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound

from .config import Settings
from .repository import (
    InvalidRecord, TableRepository, display_value, input_type, is_long_text,
)


def register_routes(app: Flask, repository: TableRepository, settings: Settings) -> None:
    """Register a small, explicit web interface against an injected repository."""

    def require_authentication():
        credentials = request.authorization
        if (
            credentials is None
            or credentials.type.lower() != "basic"
            or not hmac.compare_digest(credentials.username or "", settings.admin_username)
            or not hmac.compare_digest(credentials.password or "", settings.admin_password)
        ):
            return Response(
                "Administrator authentication required.",
                401,
                {"WWW-Authenticate": 'Basic realm="Training database", charset="UTF-8"'},
            )
        return None

    @app.before_request
    def protect_request():
        unauthorized = require_authentication()
        if unauthorized is not None:
            return unauthorized
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            expected = session.get("_csrf_token", "")
            actual = request.form.get("csrf_token", "")
            if not expected or not hmac.compare_digest(expected, actual):
                abort(400, description="Invalid or missing CSRF token")
        return None

    @app.after_request
    def protect_response(response):
        # Administrative pages may expose personnel data and must not be cached.
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        return response

    def csrf_token():
        if "_csrf_token" not in session:
            session["_csrf_token"] = secrets.token_urlsafe(32)
        return session["_csrf_token"]

    @app.context_processor
    def template_helpers():
        return {
            "navigation": repository.table_names,
            "csrf_token": csrf_token,
            "display_value": display_value,
            "input_type": input_type,
            "is_long_text": is_long_text,
        }

    @app.errorhandler(InvalidRecord)
    def handle_bad_record(error):
        return render_template("error.html", status=400, message=str(error)), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        app.logger.warning("Database rejected a row change: %s", type(error.orig).__name__)
        return render_template(
            "error.html",
            status=409,
            message="This change conflicts with an existing value or a related record.",
        ), 409

    @app.errorhandler(NotFound)
    def handle_not_found(error):
        return render_template("error.html", status=404, message=error.description), 404

    @app.get("/")
    def home():
        return redirect(url_for("table_view", table_name=repository.table_names[0]))

    @app.get("/tables/<table_name>")
    def table_view(table_name: str):
        table = repository.table(table_name)
        page = request.args.get("page", 1, type=int)
        records, has_more = repository.list_records(table_name, page)
        return render_template(
            "table.html",
            table=table,
            table_name=table_name,
            records=records,
            page=page,
            has_more=has_more,
            record_key=repository.record_key,
        )

    @app.get("/tables/<table_name>/new")
    def new_record(table_name: str):
        table = repository.table(table_name)
        return render_template(
            "form.html", table=table, table_name=table_name, record=None,
            action=url_for("create_record", table_name=table_name), title="Add record",
        )

    @app.post("/tables/<table_name>/create")
    def create_record(table_name: str):
        repository.create_record(table_name, request.form)
        return redirect(url_for("table_view", table_name=table_name), code=303)

    @app.get("/tables/<table_name>/edit/<encoded>")
    def edit_record(table_name: str, encoded: str):
        table = repository.table(table_name)
        record = repository.get_record(table_name, encoded)
        return render_template(
            "form.html", table=table, table_name=table_name, record=record,
            action=url_for("save_record", table_name=table_name, encoded=encoded),
            title="Edit record",
        )

    @app.post("/tables/<table_name>/edit/<encoded>")
    def save_record(table_name: str, encoded: str):
        repository.update_record(table_name, encoded, request.form)
        return redirect(url_for("table_view", table_name=table_name), code=303)

    @app.post("/tables/<table_name>/delete/<encoded>")
    def delete_record(table_name: str, encoded: str):
        repository.delete_record(table_name, encoded)
        return redirect(url_for("table_view", table_name=table_name), code=303)

    # Keep the original read-only table URLs while mutations use CSRF-safe POSTs.
    @app.get("/relation/<table_name>")
    @app.get("/<table_name>")
    def legacy_table_view(table_name: str):
        repository.table(table_name)
        return redirect(url_for("table_view", table_name=table_name), code=302)
