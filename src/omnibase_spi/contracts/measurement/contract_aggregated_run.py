"""ContractAggregatedRun -- run-level rollup with overall_result semantics.

Aggregates multiple ``ContractPhaseMetrics`` into a single run summary.
The ``overall_result`` field follows these semantics:

* **success** -- all mandatory phases succeeded
* **partial** -- at least one mandatory phase is missing or skipped
* **failure** -- any mandatory phase resulted in failure or error

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from omnibase_spi.contracts.measurement.contract_measurement_context import (
    ContractMeasurementContext,
)
from omnibase_spi.contracts.measurement.contract_phase_metrics import (
    ContractPhaseMetrics,
)
from omnibase_spi.contracts.measurement.contract_producer import ContractProducer


class ContractAggregatedRun(BaseModel):
    """Run-level rollup of phase metrics.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        run_id: Unique identifier for the pipeline run.
        context: Correlation identity for this run.
        producer: Identity of the aggregation producer.
        overall_result: Aggregated result (success/partial/failure).
        phase_metrics: Per-phase measurement records.
        total_duration_ms: Sum of all phase durations.
        total_cost_usd: Sum of all phase costs.
        mandatory_phases_total: Number of mandatory phases in the pipeline.
        mandatory_phases_succeeded: Number of mandatory phases that succeeded.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    run_id: str = Field(
        ...,
        description="Unique identifier for the pipeline run.",
    )
    context: ContractMeasurementContext | None = Field(
        default=None,
        description="Correlation identity for this run.",
    )
    producer: ContractProducer | None = Field(
        default=None,
        description="Identity of the aggregation producer.",
    )
    overall_result: Literal["success", "partial", "failure"] = Field(
        ...,
        description="Aggregated result (success/partial/failure).",
    )
    phase_metrics: list[ContractPhaseMetrics] = Field(
        default_factory=list,
        description="Per-phase measurement records.",
    )
    total_duration_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Sum of all phase durations.",
    )
    total_cost_usd: float | None = Field(
        default=None,
        ge=0.0,
        description="Sum of all phase costs.",
    )
    mandatory_phases_total: int = Field(
        default=0,
        ge=0,
        description="Number of mandatory phases in the pipeline.",
    )
    mandatory_phases_succeeded: int = Field(
        default=0,
        ge=0,
        description="Number of mandatory phases that succeeded.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )

    @model_validator(mode="after")
    def _validate_mandatory_phases_count(self) -> ContractAggregatedRun:
        """Ensure mandatory_phases_succeeded does not exceed mandatory_phases_total."""
        if self.mandatory_phases_succeeded > self.mandatory_phases_total:
            raise ValueError(
                "mandatory_phases_succeeded "
                f"({self.mandatory_phases_succeeded}) must not exceed "
                f"mandatory_phases_total ({self.mandatory_phases_total})"
            )
        return self
