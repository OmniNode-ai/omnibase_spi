# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Wire-format models for database service responses.

Frozen, data-only Pydantic models returned by ProtocolDatabaseService
methods. No business logic, no SPI protocol references.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

_SCHEMA_VERSION = "1.0"


class ModelQueryResult(BaseModel):
    """Result of a database query (SELECT)."""

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(default=_SCHEMA_VERSION)
    columns: list[str]
    rows: list[list[object]]
    row_count: int


class ModelExecuteResult(BaseModel):
    """Result of a database write (INSERT/UPDATE/DELETE)."""

    model_config = {"frozen": True, "extra": "allow"}

    rows_affected: int
    success: bool


class ModelTableInfo(BaseModel):
    """Metadata about a database table."""

    model_config = {"frozen": True, "extra": "allow"}

    table_name: str
    columns: list[str]
    row_count: int | None = None
    size_bytes: int | None = None


class ModelMigrationStatus(BaseModel):
    """Current migration state of the database."""

    model_config = {"frozen": True, "extra": "allow"}

    current_version: str | None = None
    pending_migrations: list[str] = []
    last_applied_at: datetime | None = None


class ModelDatabaseHealth(BaseModel):
    """Health status of a database service."""

    model_config = {"frozen": True, "extra": "allow"}

    is_healthy: bool
    latency_ms: float | None = None
    connections_active: int | None = None
    connections_idle: int | None = None
