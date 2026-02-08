"""ContractValidationPlan -- what checks to run.

Defines the set of validation checks to execute for a given pattern
candidate or pipeline phase.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContractValidationPlan(BaseModel):
    """Plan defining which validation checks to execute.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        plan_id: Unique identifier for this validation plan.
        check_ids: Ordered list of check IDs to execute.
        pattern_id: Pattern candidate this plan validates (if any).
        phase: Pipeline phase this plan applies to (if any).
        parameters: Check-specific parameter overrides keyed by check_id.
        metadata: Arbitrary metadata for the plan.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    plan_id: str = Field(
        ...,
        description="Unique identifier for this validation plan.",
    )
    check_ids: list[str] = Field(
        default_factory=list,
        description="Ordered list of check IDs to execute.",
    )
    pattern_id: str = Field(
        default="",
        description="Pattern candidate this plan validates (if any).",
    )
    phase: str = Field(
        default="",
        description="Pipeline phase this plan applies to (if any).",
    )
    parameters: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Check-specific parameter overrides keyed by check_id.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata for the plan.",
    )
