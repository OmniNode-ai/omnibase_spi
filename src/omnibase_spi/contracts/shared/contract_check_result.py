"""ContractCheckResult -- single check outcome.

Composed by RRH, validation, governance, and measurement subsystems to
represent the result of one discrete check (e.g., 'tests pass', 'lint clean',
'schema version present').

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ContractCheckResult(BaseModel):
    """Single check outcome produced by RRH, validation, governance, or measurement.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        check_id: Stable identifier for the check (e.g. RRH-1001, CHECK-PY-001).
        domain: Subsystem that produced this result.
        status: Outcome of the check.
        severity: How critical this check is considered.
        value: Machine-readable payload (score, count, etc.).
        duration_ms: Wall-clock time the check took, in milliseconds.
        message: Human-readable explanation of the result.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    check_id: str = Field(
        ...,
        description="Stable identifier for the check (e.g. RRH-1001).",
    )
    domain: Literal["rrh", "validation", "governance", "measurement"] = Field(
        ...,
        description="Subsystem that produced this result.",
    )
    status: Literal["pass", "fail", "skip"] = Field(
        ...,
        description="Outcome of the check.",
    )
    severity: Literal["critical", "major", "minor", "nit"] = Field(
        default="minor",
        description="How critical this check is considered.",
    )
    value: str | int | float | bool | None = Field(
        default=None,
        description="Machine-readable payload (score, count, etc.).",
    )
    duration_ms: float | None = Field(
        default=None,
        description="Wall-clock time the check took, in milliseconds.",
    )
    message: str = Field(
        default="",
        description="Human-readable explanation of the result.",
    )
