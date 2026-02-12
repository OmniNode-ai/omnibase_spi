"""Pipeline contracts for the ONEX hook adapter and node operation system.

These contracts define the wire formats exchanged between the shell shim,
the hook adapter, and ONEX nodes during pipeline execution.

All contracts are frozen Pydantic models with forward-compatible deserialization.
They must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

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
from omnibase_spi.enums.enum_rrh_rule import RRHRule

__all__ = [
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
]
