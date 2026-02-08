"""ContractMeasuredAttribution -- attribution with measurement composition.

Links a measurement run to its attribution chain: who produced it, what
the outcome was, and what promotion decision was made.  Composes
measurement data with attribution metadata for closed-loop tracking.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from omnibase_spi.contracts.measurement.contract_aggregated_run import (
    ContractAggregatedRun,
)
from omnibase_spi.contracts.measurement.contract_measurement_context import (
    ContractMeasurementContext,
)
from omnibase_spi.contracts.measurement.contract_promotion_gate import (
    ContractPromotionGate,
)


class ContractMeasuredAttribution(BaseModel):
    """Attribution record composed with measurement data.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        attribution_id: Unique identifier for this attribution record.
        context: Correlation identity for the measurement.
        proposed_by: Who proposed the work being measured.
        proposed_at_iso: ISO-8601 timestamp of the proposal.
        aggregated_run: The aggregated measurement run.
        promotion_gate: The promotion gate evaluation (if applicable).
        verdict: Final verdict (PASS/FAIL/QUARANTINE).
        promoted: Whether the work was promoted.
        promoted_at_iso: ISO-8601 timestamp of promotion.
        promoted_to: Target environment of promotion.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    attribution_id: str = Field(
        ...,
        description="Unique identifier for this attribution record.",
    )
    context: ContractMeasurementContext | None = Field(
        default=None,
        description="Correlation identity for the measurement.",
    )
    proposed_by: str = Field(
        default="",
        description="Who proposed the work being measured.",
    )
    proposed_at_iso: str = Field(
        default="",
        description="ISO-8601 timestamp of the proposal.",
    )
    aggregated_run: ContractAggregatedRun | None = Field(
        default=None,
        description="The aggregated measurement run.",
    )
    promotion_gate: ContractPromotionGate | None = Field(
        default=None,
        description="The promotion gate evaluation (if applicable).",
    )
    verdict: Literal["PASS", "FAIL", "QUARANTINE", ""] = Field(
        default="",
        description="Final verdict (PASS/FAIL/QUARANTINE).",
    )
    promoted: bool = Field(
        default=False,
        description="Whether the work was promoted.",
    )
    promoted_at_iso: str = Field(
        default="",
        description="ISO-8601 timestamp of promotion.",
    )
    promoted_to: str = Field(
        default="",
        description="Target environment of promotion.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )
