"""Contract definitions for omnibase_spi.

This module provides:
- **shared/**: Foundational primitives (ContractCheckResult, ContractVerdict)
- **pipeline/**: Pipeline wire-format contracts (hook invocation, node ops, auth, RRH)
- **validation/**: Validation orchestration contracts (plans, runs, results, verdicts)
- **defaults/**: YAML templates for handler contract generation

All Contract* classes are frozen Pydantic models with ``extra = "allow"``
for forward-compatible deserialization.  Every contract includes a
``schema_version`` field.

These contracts must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

# -- Shared primitives ----------------------------------------------------
# -- Pipeline contracts ---------------------------------------------------
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
from omnibase_spi.contracts.pipeline.contract_session_index import ContractSessionIndex
from omnibase_spi.contracts.pipeline.contract_work_authorization import (
    ContractWorkAuthorization,
)
from omnibase_spi.contracts.pipeline.enum_auth_reason_code import AuthReasonCode
from omnibase_spi.contracts.pipeline.enum_rrh_rule import RRHRule
from omnibase_spi.contracts.shared.contract_check_result import ContractCheckResult
from omnibase_spi.contracts.shared.contract_verdict import ContractVerdict

# -- Validation contracts -------------------------------------------------
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
    # Validation contracts
    "ContractAttributionRecord",
    "ContractPatternCandidate",
    "ContractValidationPlan",
    "ContractValidationResult",
    "ContractValidationRun",
    "ContractValidationVerdict",
    "ValidationCheck",
]
