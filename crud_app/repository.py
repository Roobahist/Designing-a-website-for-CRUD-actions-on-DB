"""Allowlisted, parameterized CRUD operations for reflected relational tables."""

from __future__ import annotations

import base64
import binascii
import math
import json
from datetime import date, datetime, time
from decimal import Decimal
from typing import Mapping

from sqlalchemy import (
    Boolean, Date, DateTime, Float, Integer, MetaData, Numeric, Text, Time,
    and_, delete, insert, inspect, select, update,
)
from sqlalchemy.engine import Engine
from werkzeug.exceptions import NotFound

# This list intentionally excludes unrelated tables that may share the database.
SUPPORTED_TABLES = (
    "department", "role", "employee", "skill", "teacher", "course",
    "course_class_days", "course_gives_skill", "employee_has_skill",
    "employee_attends_course", "employee_takes_exam",
)


class InvalidRecord(ValueError):
    """User-supplied row data or record identity is invalid."""


def input_type(column) -> str:
    datatype = column.type
    if isinstance(datatype, DateTime):
        return "datetime-local"
    if isinstance(datatype, Date):
        return "date"
    if isinstance(datatype, Time):
        return "time"
    if isinstance(datatype, (Integer, Numeric, Float)):
        return "number"
    return "text"


def is_long_text(column) -> bool:
    return isinstance(column.type, Text)


def display_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (date, datetime, time)):
        return value.isoformat(timespec="seconds") if isinstance(value, (time, datetime)) else value.isoformat()
    return str(value)


def _convert(column, value: str):
    if value == "":
        if column.nullable:
            return None
        raise InvalidRecord(f"{column.name} cannot be empty")
    datatype = column.type
    try:
        if isinstance(datatype, Boolean):
            if value.lower() not in {"0", "1", "true", "false"}:
                raise ValueError("invalid boolean")
            return value.lower() in {"1", "true"}
        if isinstance(datatype, Integer):
            return int(value)
        if isinstance(datatype, Float):
            number = float(value)
            if not math.isfinite(number):
                raise ValueError("non-finite number")
            return number
        if isinstance(datatype, Numeric):
            return Decimal(value)
        if isinstance(datatype, DateTime):
            return datetime.fromisoformat(value)
        if isinstance(datatype, Date):
            return date.fromisoformat(value)
        if isinstance(datatype, Time):
            return time.fromisoformat(value)
    except (ValueError, TypeError, ArithmeticError) as exc:
        raise InvalidRecord(f"Invalid value for {column.name}") from exc
    return value


class TableRepository:
    """Reflect only the known schema and share one engine across requests."""

    def __init__(self, engine: Engine, page_size: int = 50):
        self.engine = engine
        self.page_size = page_size
        available = set(inspect(engine).get_table_names())
        names = [name for name in SUPPORTED_TABLES if name in available]
        if not names:
            raise RuntimeError("No supported tables found. Initialize the database schema first.")
        metadata = MetaData()
        metadata.reflect(bind=engine, only=names)
        self.tables = {name: metadata.tables[name] for name in names}
        self.table_names = tuple(names)
        if any(not table.primary_key.columns for table in self.tables.values()):
            raise RuntimeError("Every managed table must have a primary key")

    def table(self, name: str):
        if name not in self.tables:
            raise NotFound("Unknown table")
        return self.tables[name]

    def list_records(self, name: str, page: int = 1):
        if page < 1 or page > 10_000:
            raise InvalidRecord("Page number out of range")
        table = self.table(name)
        stmt = (
            select(table)
            .order_by(*table.primary_key.columns)
            .limit(self.page_size + 1)
            .offset((page - 1) * self.page_size)
        )
        with self.engine.connect() as connection:
            rows = [dict(row) for row in connection.execute(stmt).mappings()]
        return rows[: self.page_size], len(rows) > self.page_size

    def record_key(self, name: str, record: Mapping) -> str:
        table = self.table(name)
        values = [str(record[column.name]) for column in table.primary_key.columns]
        payload = json.dumps(values, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")

    def _identity_clause(self, table, encoded: str):
        if len(encoded) > 4096:
            raise InvalidRecord("Invalid record identifier")
        try:
            padded = encoded + "=" * (-len(encoded) % 4)
            decoded = base64.b64decode(padded, altchars=b"-_", validate=True)
            values = json.loads(decoded.decode("utf-8"))
        except (ValueError, UnicodeError, binascii.Error) as exc:
            raise InvalidRecord("Invalid record identifier") from exc
        keys = list(table.primary_key.columns)
        if not isinstance(values, list) or len(values) != len(keys):
            raise InvalidRecord("Invalid record identifier")
        if not all(isinstance(value, str) for value in values):
            raise InvalidRecord("Invalid record identifier")
        return and_(*(
            column == _convert(column, value)
            for column, value in zip(keys, values, strict=True)
        ))

    def get_record(self, name: str, encoded: str):
        table = self.table(name)
        where = self._identity_clause(table, encoded)
        with self.engine.connect() as connection:
            record = connection.execute(select(table).where(where)).mappings().first()
        if record is None:
            raise NotFound("Record not found")
        return dict(record)

    def _payload(self, table, form: Mapping[str, str], *, editing: bool):
        columns = [col for col in table.columns if not (editing and col.primary_key)]
        allowed = {col.name for col in columns} | {"csrf_token"}
        unexpected = set(form.keys()) - allowed
        if unexpected:
            raise InvalidRecord("Unexpected fields: " + ", ".join(sorted(unexpected)))
        values = {}
        for column in columns:
            value = form.get(column.name, "")
            if value == "" and (column.default is not None or column.server_default is not None):
                continue
            values[column.name] = _convert(column, value)
        return values

    def create_record(self, name: str, form: Mapping[str, str]):
        table = self.table(name)
        payload = self._payload(table, form, editing=False)
        with self.engine.begin() as connection:
            connection.execute(insert(table).values(payload))

    def update_record(self, name: str, encoded: str, form: Mapping[str, str]):
        table = self.table(name)
        where = self._identity_clause(table, encoded)
        payload = self._payload(table, form, editing=True)
        with self.engine.begin() as connection:
            if connection.execute(select(table).where(where)).first() is None:
                raise NotFound("Record not found")
            if payload:
                connection.execute(update(table).where(where).values(payload))

    def delete_record(self, name: str, encoded: str):
        table = self.table(name)
        where = self._identity_clause(table, encoded)
        with self.engine.begin() as connection:
            result = connection.execute(delete(table).where(where))
            if result.rowcount == 0:
                raise NotFound("Record not found")
