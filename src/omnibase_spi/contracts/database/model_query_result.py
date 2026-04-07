# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ModelQueryResult -- wire-format contract for database query results.

Returned by ProtocolDatabaseConnection.execute_query() and execute_command().

This module MUST NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ModelQueryResult(BaseModel):
    """Wire-format representation of a database query result.

    Attributes:
        rows: List of row dictionaries (column name to value).
        columns: Ordered list of column names in the result set.
        row_count: Number of rows returned or affected.
        duration_ms: Query execution time in milliseconds.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    rows: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of row dictionaries (column name to value).",
    )
    columns: list[str] = Field(
        default_factory=list,
        description="Ordered list of column names in the result set.",
    )
    row_count: int = Field(
        ...,
        description="Number of rows returned or affected.",
    )
    duration_ms: float = Field(
        ...,
        description="Query execution time in milliseconds.",
    )
