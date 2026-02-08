"""ContractNodeError -- structured error with error_code, message, retryable.

A lightweight, structured error envelope returned by ONEX nodes and
pipeline components when an operation fails.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContractNodeError(BaseModel):
    """Structured error produced by an ONEX node or pipeline component.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        error_code: Machine-readable error code (e.g. NODE-TIMEOUT, AUTH-DENIED).
        message: Human-readable error description.
        retryable: Whether the caller should retry the operation.
        details: Arbitrary structured details for debugging.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    error_code: str = Field(
        ...,
        description="Machine-readable error code (e.g. NODE-TIMEOUT).",
    )
    message: str = Field(
        default="",
        description="Human-readable error description.",
    )
    retryable: bool = Field(
        default=False,
        description="Whether the caller should retry the operation.",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary structured details for debugging.",
    )
