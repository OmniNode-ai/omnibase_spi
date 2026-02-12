"""Contract definitions for omnibase_spi.

This module provides:
- **shared/**: Foundational primitives (ContractCheckResult, ContractVerdict)
- **pipeline/**: Pipeline wire-format contracts (hook invocation, node ops, auth, RRH)
- **validation/**: Validation orchestration contracts (plans, runs, results, verdicts)
- **measurement/**: Measurement pipeline contracts (phase metrics, promotion gates)
- **defaults/**: YAML templates for handler contract generation

All Contract* classes are frozen Pydantic models.  Most use ``extra = "allow"``
for forward-compatible deserialization; measurement contracts use
``extra = "forbid"`` + explicit ``extensions`` field for high-integrity gating.
Every contract includes a ``schema_version`` field.

These contracts must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

# Measurement contracts
from omnibase_spi.contracts.measurement.contract_aggregated_run import (
    ContractAggregatedRun,
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
from omnibase_spi.contracts.pipeline.contract_artifact_pointer import (
    ContractArtifactPointer,
)
from omnibase_spi.contracts.pipeline.contract_auth_gate_input import (
    ContractAuthGateInput,
)
from omnibase_spi.contracts.pipeline.contract_checkpoint import ContractCheckpoint
from omnibase_spi.contracts.pipeline.contract_execution_context import (
    ContractExecutionContext,
)
from omnibase_spi.contracts.pipeline.contract_hook_invocation import (
    ContractHookInvocation,
)
from omnibase_spi.contracts.pipeline.contract_hook_invocation_result import (
    ContractHookInvocationResult,
)
from omnibase_spi.contracts.pipeline.contract_node_error import ContractNodeError
from omnibase_spi.contracts.pipeline.contract_node_operation_request import (
    ContractNodeOperationRequest,
)
from omnibase_spi.contracts.pipeline.contract_node_operation_result import (
    ContractNodeOperationResult,
)
from omnibase_spi.contracts.pipeline.contract_repo_scope import ContractRepoScope
from omnibase_spi.contracts.pipeline.contract_rrh_result import ContractRRHResult
from omnibase_spi.contracts.pipeline.contract_run_context import ContractRunContext
from omnibase_spi.contracts.pipeline.contract_schema_compat import (
    SchemaVersion,
    is_compatible,
)
from omnibase_spi.contracts.pipeline.contract_session_index import ContractSessionIndex
from omnibase_spi.contracts.pipeline.contract_wire_codec import (
    from_json,
    from_yaml,
    to_json,
    to_yaml,
)
from omnibase_spi.contracts.pipeline.contract_work_authorization import (
    ContractWorkAuthorization,
)
from omnibase_spi.contracts.pipeline.enum_auth_reason_code import AuthReasonCode
from omnibase_spi.contracts.shared.contract_check_result import ContractCheckResult
from omnibase_spi.contracts.shared.contract_verdict import ContractVerdict
from omnibase_spi.contracts.validation.contract_attribution_record import (
    ContractAttributionRecord,
)
from omnibase_spi.contracts.validation.contract_pattern_candidate import (
    ContractPatternCandidate,
)
from omnibase_spi.contracts.validation.contract_validation_plan import (
    ContractValidationPlan,
)
from omnibase_spi.contracts.validation.contract_validation_result import (
    ContractValidationResult,
)
from omnibase_spi.contracts.validation.contract_validation_run import (
    ContractValidationRun,
)
from omnibase_spi.contracts.validation.contract_validation_verdict import (
    ContractValidationVerdict,
)
from omnibase_spi.contracts.validation.enum_validation_check import ValidationCheck
from omnibase_spi.enums.enum_rrh_rule import RRHRule

__all__ = [
    # Shared primitives
    "ContractCheckResult",
    "ContractVerdict",
    # Pipeline contracts
    "ContractArtifactPointer",
    "ContractAuthGateInput",
    "ContractCheckpoint",
    "ContractExecutionContext",
    "ContractHookInvocation",
    "ContractHookInvocationResult",
    "ContractNodeError",
    "ContractNodeOperationRequest",
    "ContractNodeOperationResult",
    "ContractRepoScope",
    "ContractRRHResult",
    "ContractRunContext",
    "ContractSessionIndex",
    "ContractWorkAuthorization",
    "AuthReasonCode",
    "RRHRule",
    # Wire-format utilities
    "SchemaVersion",
    "is_compatible",
    "to_json",
    "from_json",
    "to_yaml",
    "from_yaml",
    # Validation contracts
    "ContractAttributionRecord",
    "ContractPatternCandidate",
    "ContractValidationPlan",
    "ContractValidationResult",
    "ContractValidationRun",
    "ContractValidationVerdict",
    "ValidationCheck",
    # Measurement contracts - enums
    "ContractEnumPipelinePhase",
    "ContractEnumResultClassification",
    "MeasurementCheck",
    # Measurement contracts - core
    "ContractMeasurementContext",
    "ContractProducer",
    # Measurement contracts - standalone helpers
    "derive_baseline_key",
    # Measurement contracts - phase metrics and sub-contracts
    "ContractArtifactPointerMeasurement",
    "ContractCostMetrics",
    "ContractDurationMetrics",
    "ContractOutcomeMetrics",
    "ContractPhaseMetrics",
    "ContractTestMetrics",
    # Measurement contracts - domain envelope
    "ContractMeasurementEvent",
    # Measurement contracts - aggregation and promotion
    "ContractAggregatedRun",
    "ContractDimensionEvidence",
    "ContractPromotionGate",
    # Measurement contracts - attribution
    "ContractMeasuredAttribution",
]
