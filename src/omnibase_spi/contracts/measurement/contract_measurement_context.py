"""ContractMeasurementContext -- correlation identity for measurements.

Captures the full correlation identity for a measurement: which ticket,
repo, toolchain, strictness level, scenario, and pattern are being
measured.

The module-level ``derive_baseline_key`` function deterministically
derives a SHA-256 baseline key from a ``ContractMeasurementContext``
instance.  It is a standalone function (not a method) so that the
contract model remains a pure data object with no business logic.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

import hashlib
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ContractMeasurementContext(BaseModel):
    """Correlation identity for measurement tracking.

    The baseline key is deterministically derived from the combination
    of ticket_id, repo_id, toolchain, strictness, scenario_id, and
    pattern_id fields.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        ticket_id: Ticket or work-item identifier (e.g. OMN-2024).
        repo_id: Repository identifier (e.g. omnibase_spi).
        toolchain: Toolchain used for execution (e.g. poetry, npm).
        strictness: Strictness level (e.g. strict, lenient, default).
        scenario_id: Scenario identifier for parameterised runs.
        pattern_id: Pattern identifier when measuring a specific pattern.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    ticket_id: str = Field(
        ...,
        description="Ticket or work-item identifier (e.g. OMN-2024).",
    )
    repo_id: str = Field(
        default="",
        description="Repository identifier (e.g. omnibase_spi).",
    )
    toolchain: str = Field(
        default="",
        description="Toolchain used for execution (e.g. poetry, npm).",
    )
    strictness: str = Field(
        default="default",
        description="Strictness level (e.g. strict, lenient, default).",
    )
    scenario_id: str = Field(
        default="",
        description="Scenario identifier for parameterised runs.",
    )
    pattern_id: str = Field(
        default="",
        description="Pattern identifier when measuring a specific pattern.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )


def derive_baseline_key(ctx: ContractMeasurementContext) -> str:
    """Derive a deterministic baseline key from context fields.

    This is a standalone function rather than a method on the contract
    model so that ``ContractMeasurementContext`` remains a pure,
    frozen data object with no business logic.

    Args:
        ctx: The measurement context whose identity fields are hashed.

    Returns:
        A hex-encoded SHA-256 hash of the concatenated identity fields.
    """
    parts = [
        ctx.ticket_id,
        ctx.repo_id,
        ctx.toolchain,
        ctx.strictness,
        ctx.scenario_id,
        ctx.pattern_id,
    ]
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
