"""ContractPhaseMetrics -- primary measurement unit.

The core measurement record for a single pipeline phase execution.
Composed of sub-contracts for duration, cost, outcome, and test metrics,
plus structured artifact pointers.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from omnibase_spi.contracts.measurement.contract_measurement_context import (
    ContractMeasurementContext,
)
from omnibase_spi.contracts.measurement.contract_producer import ContractProducer
from omnibase_spi.contracts.measurement.enum_pipeline_phase import (
    ContractEnumPipelinePhase,
)
from omnibase_spi.contracts.measurement.enum_result_classification import (
    ContractEnumResultClassification,
)

# -- Sub-contracts -----------------------------------------------------------


class ContractArtifactPointerMeasurement(BaseModel):
    """Reference to an artifact produced during measurement.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        artifact_type: Type of artifact (e.g. 'file', 'pr', 'commit').
        name: Human-readable name for the artifact.
        uri: URI or path to the artifact.
        checksum: Optional checksum for integrity verification.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    artifact_type: str = Field(
        ...,
        description="Type of artifact (e.g. 'file', 'pr', 'commit').",
    )
    name: str = Field(
        default="",
        description="Human-readable name for the artifact.",
    )
    uri: str = Field(
        default="",
        description="URI or path to the artifact.",
    )
    checksum: str = Field(
        default="",
        description="Optional checksum for integrity verification.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )


class ContractDurationMetrics(BaseModel):
    """Duration measurements for a phase.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        wall_clock_ms: Total wall-clock time in milliseconds.
        cpu_ms: CPU time in milliseconds (if available).
        queue_ms: Time spent waiting in queue before execution.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    wall_clock_ms: float = Field(
        ...,
        ge=0.0,
        description="Total wall-clock time in milliseconds.",
    )
    cpu_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="CPU time in milliseconds (if available).",
    )
    queue_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Time spent waiting in queue before execution.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )


class ContractCostMetrics(BaseModel):
    """Cost measurements for a phase.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        llm_input_tokens: Number of input tokens consumed by LLM calls.
        llm_output_tokens: Number of output tokens produced by LLM calls.
        llm_total_tokens: Total tokens (input + output).
        estimated_cost_usd: Estimated cost in USD.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    llm_input_tokens: int = Field(
        default=0,
        ge=0,
        description="Number of input tokens consumed by LLM calls.",
    )
    llm_output_tokens: int = Field(
        default=0,
        ge=0,
        description="Number of output tokens produced by LLM calls.",
    )
    llm_total_tokens: int = Field(
        default=0,
        ge=0,
        description="Total tokens (input + output).",
    )
    estimated_cost_usd: float | None = Field(
        default=None,
        ge=0.0,
        description="Estimated cost in USD.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )


class ContractOutcomeMetrics(BaseModel):
    """Outcome measurements for a phase.

    The ``skip_reason_code`` field is required (non-empty) when
    ``result_classification`` is ``skipped``.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        result_classification: Phase result category.
        error_messages: Sanitised error messages (no secrets).
        error_codes: Machine-stable error codes.
        failed_tests: Names of failed test cases.
        skip_reason: Human-readable reason for skipping.
        skip_reason_code: Machine-stable skip reason (required when skipped).
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    result_classification: ContractEnumResultClassification = Field(
        ...,
        description="Phase result category.",
    )
    error_messages: list[str] = Field(
        default_factory=list,
        description="Sanitised error messages (no secrets).",
    )
    error_codes: list[str] = Field(
        default_factory=list,
        description="Machine-stable error codes.",
    )
    failed_tests: list[str] = Field(
        default_factory=list,
        description="Names of failed test cases.",
    )
    skip_reason: str = Field(
        default="",
        description="Human-readable reason for skipping.",
    )
    skip_reason_code: str = Field(
        default="",
        description="Machine-stable skip reason (required when skipped).",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )

    @model_validator(mode="after")
    def _validate_skip_reason_code(self) -> ContractOutcomeMetrics:
        """Ensure skip_reason_code is non-empty when classification is skipped."""
        if (
            self.result_classification == ContractEnumResultClassification.SKIPPED
            and not self.skip_reason_code
        ):
            raise ValueError(
                "skip_reason_code must be non-empty when "
                "result_classification is 'skipped'"
            )
        return self


class ContractTestMetrics(BaseModel):
    """Test execution measurements for a phase.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        total_tests: Total number of tests executed.
        passed_tests: Number of tests that passed.
        failed_tests: Number of tests that failed.
        skipped_tests: Number of tests that were skipped.
        error_tests: Number of tests that errored.
        pass_rate: Pass rate as a fraction (0.0 to 1.0).
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    total_tests: int = Field(
        default=0,
        ge=0,
        description="Total number of tests executed.",
    )
    passed_tests: int = Field(
        default=0,
        ge=0,
        description="Number of tests that passed.",
    )
    failed_tests: int = Field(
        default=0,
        ge=0,
        description="Number of tests that failed.",
    )
    skipped_tests: int = Field(
        default=0,
        ge=0,
        description="Number of tests that were skipped.",
    )
    error_tests: int = Field(
        default=0,
        ge=0,
        description="Number of tests that errored.",
    )
    pass_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Pass rate as a fraction (0.0 to 1.0).",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )


# -- Primary contract --------------------------------------------------------


class ContractPhaseMetrics(BaseModel):
    """Primary measurement unit for a single pipeline phase execution.

    Composed of sub-contracts for duration, cost, outcome, and test
    metrics, plus structured artifact pointers and correlation context.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        run_id: Unique identifier for the pipeline run.
        phase: Pipeline phase this measurement covers.
        phase_id: Unique identifier for this phase execution.
        attempt: Attempt number (1-based) for retried phases.
        context: Correlation identity for this measurement.
        producer: Identity of the measurement producer.
        duration: Duration metrics for the phase.
        cost: Cost metrics for the phase.
        outcome: Outcome metrics for the phase.
        tests: Test execution metrics for the phase.
        artifact_pointers: Structured references to produced artifacts.
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
    phase: ContractEnumPipelinePhase = Field(
        ...,
        description="Pipeline phase this measurement covers.",
    )
    phase_id: str = Field(
        default="",
        description="Unique identifier for this phase execution.",
    )
    attempt: int = Field(
        default=1,
        ge=1,
        description="Attempt number (1-based) for retried phases.",
    )
    context: ContractMeasurementContext | None = Field(
        default=None,
        description="Correlation identity for this measurement.",
    )
    producer: ContractProducer | None = Field(
        default=None,
        description="Identity of the measurement producer.",
    )
    duration: ContractDurationMetrics | None = Field(
        default=None,
        description="Duration metrics for the phase.",
    )
    cost: ContractCostMetrics | None = Field(
        default=None,
        description="Cost metrics for the phase.",
    )
    outcome: ContractOutcomeMetrics | None = Field(
        default=None,
        description="Outcome metrics for the phase.",
    )
    tests: ContractTestMetrics | None = Field(
        default=None,
        description="Test execution metrics for the phase.",
    )
    artifact_pointers: list[ContractArtifactPointerMeasurement] = Field(
        default_factory=list,
        description="Structured references to produced artifacts.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )
