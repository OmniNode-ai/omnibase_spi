"""ContractPromotionGate -- evidence-tier gate for promotion decisions.

Defines the evidence required and observed for a promotion decision.
Each dimension has its own evidence record with per-dimension sufficiency
rather than a single record-count threshold.

The ``baseline_key`` is deterministically derived from
:class:`ContractMeasurementContext`.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from omnibase_spi.contracts.measurement.contract_measurement_context import (
    ContractMeasurementContext,
)


class ContractDimensionEvidence(BaseModel):
    """Evidence for a single promotion dimension.

    When ``baseline_value`` is 0, ``delta_pct`` is ``None`` (division
    by zero is not meaningful).

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        dimension: Name of the dimension (e.g. 'test_pass_rate', 'cost').
        baseline_value: Baseline measurement value.
        current_value: Current measurement value.
        delta_pct: Percentage change from baseline (None when baseline is 0).
        threshold: Required threshold for sufficiency.
        sufficient: Whether this dimension meets the threshold.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    dimension: str = Field(
        ...,
        description="Name of the dimension (e.g. 'test_pass_rate', 'cost').",
    )
    baseline_value: float = Field(
        default=0.0,
        description="Baseline measurement value.",
    )
    current_value: float = Field(
        default=0.0,
        description="Current measurement value.",
    )
    delta_pct: float | None = Field(
        default=None,
        description="Percentage change from baseline (None when baseline is 0).",
    )
    threshold: float | None = Field(
        default=None,
        description="Required threshold for sufficiency.",
    )
    sufficient: bool = Field(
        default=False,
        description="Whether this dimension meets the threshold.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )

    @model_validator(mode="after")
    def _validate_delta_pct_with_zero_baseline(self) -> ContractDimensionEvidence:
        """Ensure delta_pct is None when baseline_value is 0."""
        if self.baseline_value == 0.0 and self.delta_pct is not None:
            raise ValueError(
                "delta_pct must be None when baseline_value is 0 "
                "(division by zero is not meaningful)"
            )
        return self


class ContractPromotionGate(BaseModel):
    """Evidence-tier gate for promotion decisions.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        run_id: Pipeline run this gate evaluates.
        context: Measurement context used for baseline key derivation.
        baseline_key: Deterministic key derived from context.
        gate_result: Overall gate result (pass/fail/insufficient_evidence).
        dimensions: Per-dimension evidence records.
        required_dimensions: Names of dimensions that must be sufficient.
        sufficient_count: Number of dimensions that are sufficient.
        total_count: Total number of dimensions evaluated.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    run_id: str = Field(
        ...,
        description="Pipeline run this gate evaluates.",
    )
    context: ContractMeasurementContext | None = Field(
        default=None,
        description="Measurement context used for baseline key derivation.",
    )
    baseline_key: str = Field(
        default="",
        description="Deterministic key derived from context.",
    )
    gate_result: Literal["pass", "fail", "insufficient_evidence"] = Field(
        ...,
        description="Overall gate result (pass/fail/insufficient_evidence).",
    )
    dimensions: list[ContractDimensionEvidence] = Field(
        default_factory=list,
        description="Per-dimension evidence records.",
    )
    required_dimensions: list[str] = Field(
        default_factory=list,
        description="Names of dimensions that must be sufficient.",
    )
    sufficient_count: int = Field(
        default=0,
        ge=0,
        description="Number of dimensions that are sufficient.",
    )
    total_count: int = Field(
        default=0,
        ge=0,
        description="Total number of dimensions evaluated.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )

    @model_validator(mode="after")
    def _validate_sufficient_count(self) -> ContractPromotionGate:
        """Ensure sufficient_count does not exceed total_count."""
        if self.sufficient_count > self.total_count:
            raise ValueError(
                f"sufficient_count ({self.sufficient_count}) must not exceed "
                f"total_count ({self.total_count})"
            )
        return self
