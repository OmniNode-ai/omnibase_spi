"""ContractVerdict -- aggregated outcome.

Represents the aggregated verdict (PASS / FAIL / QUARANTINE) computed
from a collection of :class:`ContractCheckResult` instances.  Used by
both RRH and validation subsystems.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ContractVerdict(BaseModel):
    """Aggregated outcome from multiple check results.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        status: Overall verdict.
        score: Numeric quality score (0 = worst, 100 = best).
        block_reasons: List of human-readable reasons that block promotion.
        human_summary: One-paragraph summary suitable for PR comments.
        promotion_recommendation: Whether this artifact should be promoted.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    status: Literal["PASS", "FAIL", "QUARANTINE"] = Field(
        ...,
        description="Overall verdict.",
    )
    score: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Numeric quality score (0 = worst, 100 = best).",
    )
    block_reasons: list[str] = Field(
        default_factory=list,
        description="Human-readable reasons that block promotion.",
    )
    human_summary: str = Field(
        default="",
        description="One-paragraph summary suitable for PR comments.",
    )
    promotion_recommendation: bool = Field(
        default=False,
        description="Whether this artifact should be promoted.",
    )
