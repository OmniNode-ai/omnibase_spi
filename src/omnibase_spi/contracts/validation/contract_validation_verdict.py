"""ContractValidationVerdict -- composes ContractVerdict + promotion.

The final verdict of a validation run, combining the aggregated verdict
with promotion recommendation and any additional validation-specific
context.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from omnibase_spi.contracts.shared.contract_verdict import ContractVerdict


class ContractValidationVerdict(BaseModel):
    """Final verdict from a validation run with promotion recommendation.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        run_id: Correlation ID linking to the validation run.
        verdict: Aggregated verdict from all checks.
        pattern_id: Pattern candidate that was validated (if any).
        promote: Whether the pattern should be promoted.
        promotion_target: Where the pattern should be promoted to.
        notes: Human-readable notes about the verdict.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    run_id: str = Field(
        default="",
        description="Correlation ID linking to the validation run.",
    )
    verdict: ContractVerdict = Field(
        ...,
        description="Aggregated verdict from all checks.",
    )
    pattern_id: str = Field(
        default="",
        description="Pattern candidate that was validated (if any).",
    )
    promote: bool = Field(
        default=False,
        description="Whether the pattern should be promoted.",
    )
    promotion_target: str = Field(
        default="",
        description="Where the pattern should be promoted to.",
    )
    notes: str = Field(
        default="",
        description="Human-readable notes about the verdict.",
    )
