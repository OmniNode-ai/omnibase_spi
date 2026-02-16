"""ContractComplianceResult -- quality gate outcome for delegation responses.

Captures the outcome of a quality-gate evaluation applied to a delegated
response.  Used by :class:`ContractDelegatedResponse` to attach compliance
metadata alongside the rendered output.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ContractComplianceResult(BaseModel):
    """Outcome of a quality-gate evaluation on a delegation response.

    Note:
        ``passed`` is the boolean summary and ``verdict`` provides the full
        qualitative result.  These fields are intentionally independent so that
        producers can express nuanced outcomes (e.g. ``passed=True`` with
        ``verdict='WARN'``).  Consumers should treat ``passed`` as
        authoritative for boolean checks and ``verdict`` for detailed
        assessment.  Cross-field consistency validation is deferred to
        consumers.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        passed: Whether the quality gate passed.
        gate_name: Name of the quality gate that was evaluated.
        score: Numeric quality score (0.0-1.0).
        threshold: Minimum score required to pass.
        verdict: Categorical verdict of the evaluation.
        violations: List of violation descriptions if the gate failed.
        evaluated_at_iso: ISO-8601 timestamp of the evaluation.
            Format validation is deferred to consumers.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    passed: bool = Field(
        ...,
        description="Whether the quality gate passed.",
    )
    gate_name: str = Field(
        default="",
        description="Name of the quality gate that was evaluated.",
    )
    score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Numeric quality score (0.0-1.0).",
    )
    threshold: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum score required to pass.",
    )
    verdict: Literal["PASS", "FAIL", "WARN", "SKIP"] = Field(
        default="SKIP",
        description="Categorical verdict of the evaluation.",
    )
    violations: list[str] = Field(
        default_factory=list,
        description="List of violation descriptions if the gate failed.",
    )
    evaluated_at_iso: str = Field(
        default="",
        description=(
            "ISO-8601 timestamp of the evaluation.  "
            "Format validation is deferred to consumers."
        ),
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )
