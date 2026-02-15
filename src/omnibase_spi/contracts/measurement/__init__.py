"""Measurement contracts for the ONEX measurement pipeline.

This module provides frozen, high-integrity wire-format contracts for
measurement tracking across pipeline phases.  All measurement contracts
use ``ConfigDict(frozen=True, extra="forbid")`` with an explicit
``extensions: dict[str, Any]`` escape hatch, diverging from the SPI
``extra="allow"`` convention because measurement data feeds promotion
gates where silent field acceptance creates drift.

These contracts must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from omnibase_spi.contracts.measurement.contract_aggregated_run import (
    ContractAggregatedRun,
)
from omnibase_spi.contracts.measurement.contract_llm_call_metrics import (
    ContractLlmCallMetrics,
    ContractLlmUsageNormalized,
    ContractLlmUsageRaw,
)
from omnibase_spi.contracts.measurement.contract_measured_attribution import (
    ContractMeasuredAttribution,
)
from omnibase_spi.contracts.measurement.contract_measurement_context import (
    ContractMeasurementContext,
    derive_baseline_key,
)
from omnibase_spi.contracts.measurement.contract_measurement_event import (
    ContractMeasurementEvent,
)
from omnibase_spi.contracts.measurement.contract_phase_metrics import (
    ContractArtifactPointerMeasurement,
    ContractCostMetrics,
    ContractDurationMetrics,
    ContractOutcomeMetrics,
    ContractPhaseMetrics,
    ContractTestMetrics,
)
from omnibase_spi.contracts.measurement.contract_producer import ContractProducer
from omnibase_spi.contracts.measurement.contract_promotion_gate import (
    ContractDimensionEvidence,
    ContractPromotionGate,
)
from omnibase_spi.contracts.measurement.enum_measurement_check import MeasurementCheck
from omnibase_spi.contracts.measurement.enum_pipeline_phase import (
    ContractEnumPipelinePhase,
)
from omnibase_spi.contracts.measurement.enum_result_classification import (
    ContractEnumResultClassification,
)
from omnibase_spi.contracts.measurement.enum_usage_source import (
    ContractEnumUsageSource,
)

__all__ = [
    "ContractAggregatedRun",
    "ContractArtifactPointerMeasurement",
    "ContractCostMetrics",
    "ContractDimensionEvidence",
    "ContractDurationMetrics",
    "ContractEnumPipelinePhase",
    "ContractEnumResultClassification",
    "ContractEnumUsageSource",
    "ContractLlmCallMetrics",
    "ContractLlmUsageNormalized",
    "ContractLlmUsageRaw",
    "ContractMeasuredAttribution",
    "ContractMeasurementContext",
    "ContractMeasurementEvent",
    "ContractOutcomeMetrics",
    "ContractPhaseMetrics",
    "ContractProducer",
    "ContractPromotionGate",
    "ContractTestMetrics",
    "MeasurementCheck",
    "derive_baseline_key",
]
