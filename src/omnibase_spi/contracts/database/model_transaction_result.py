# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ModelTransactionResult -- wire-format contract for database transaction results.

Returned by ProtocolDatabaseConnection.execute_transaction().

This module MUST NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModelTransactionResult(BaseModel):
    """Wire-format representation of a database transaction outcome.

    Attributes:
        committed: Whether the transaction was committed successfully.
        operations_count: Number of operations executed within the transaction.
        duration_ms: Total transaction execution time in milliseconds.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    committed: bool = Field(
        ...,
        description="Whether the transaction was committed successfully.",
    )
    operations_count: int = Field(
        ...,
        description="Number of operations executed within the transaction.",
    )
    duration_ms: float = Field(
        ...,
        description="Total transaction execution time in milliseconds.",
    )
