"""Validated configuration for the CRUD administration application."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Settings:
    database_url: str
    admin_password: str
    secret_key: str
    admin_username: str = "admin"
    page_size: int = 50
    cookie_secure: bool = False

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        values = os.environ if env is None else env
        required = ("DATABASE_URL", "CRUD_ADMIN_PASSWORD", "FLASK_SECRET_KEY")
        missing = [name for name in required if not values.get(name)]
        if missing:
            raise ValueError("Missing required environment variables: " + ", ".join(missing))

        secret = values["FLASK_SECRET_KEY"]
        password = values["CRUD_ADMIN_PASSWORD"]
        if len(secret) < 32:
            raise ValueError("FLASK_SECRET_KEY must contain at least 32 characters")
        if len(password) < 12:
            raise ValueError("CRUD_ADMIN_PASSWORD must contain at least 12 characters")

        try:
            page_size = int(values.get("PAGE_SIZE", "50"))
        except ValueError as exc:
            raise ValueError("PAGE_SIZE must be an integer") from exc
        if not 1 <= page_size <= 200:
            raise ValueError("PAGE_SIZE must be between 1 and 200")

        secure = values.get("COOKIE_SECURE", "false").lower()
        if secure not in ("true", "false"):
            raise ValueError("COOKIE_SECURE must be true or false")

        return cls(
            database_url=values["DATABASE_URL"],
            admin_password=password,
            secret_key=secret,
            admin_username=values.get("CRUD_ADMIN_USERNAME", "admin"),
            page_size=page_size,
            cookie_secure=secure == "true",
        )
