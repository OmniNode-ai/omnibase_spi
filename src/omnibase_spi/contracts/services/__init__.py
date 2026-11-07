# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Wire-format contract models for external service adapters.

Frozen, data-only Pydantic models that define the return types used by
service protocols (source control, project tracking, database, etc.).
These models carry no business logic and are safe to use across process
boundaries.
"""

from omnibase_spi.contracts.services.contract_database_service_types import (
    ModelDatabaseHealth,
    ModelExecuteResult,
    ModelMigrationStatus,
    ModelQueryResult,
    ModelTableInfo,
)
from omnibase_spi.contracts.services.contract_project_tracker_types import (
    ModelComment,
    ModelIssue,
    ModelProject,
)
from omnibase_spi.contracts.services.contract_source_control_types import (
    ModelBranch,
    ModelCheckRun,
    ModelCIStatus,
    ModelDiff,
    ModelMergeResult,
    ModelPullRequest,
)
from omnibase_spi.contracts.services.model_floor_ticket_store_types import (
    ModelFloorTicketCreateRequest,
    ModelFloorTicketCreateResult,
    ModelFloorTicketLookupRequest,
    ModelFloorTicketLookupResult,
    ModelFloorTicketSearchRequest,
    ModelFloorTicketSearchResult,
)
from omnibase_spi.contracts.services.model_host_call_types import (
    ModelHostCallAnswer,
    ModelHostCallRequest,
)
from omnibase_spi.contracts.services.model_lane_host_pool_types import (
    ModelLaneHostPoolReading,
    ModelLaneHostPoolRequest,
    ModelLaneHostPoolSnapshot,
)
from omnibase_spi.contracts.services.model_lane_host_provisioning_types import (
    ModelLaneChangeList,
    ModelLaneCloseoutCells,
    ModelLaneHostStepRequest,
    ModelLaneHostStepResult,
    ModelLaneLedgerOutboxRows,
    ModelLanePluginTree,
    ModelLaneRegistryRootResult,
    ModelLaneRunDirsResult,
    ModelLaneShipPluginTreesRequest,
    ModelLaneShipPluginTreesResult,
    ModelLaneStagedInput,
    ModelLaneStageInputRequest,
)
from omnibase_spi.contracts.services.model_lane_host_transport_types import (
    ModelLaneHostRef,
    ModelLanePrepareWorktreeRequest,
    ModelLanePrepareWorktreeResult,
    ModelLaneReadEngineExitRequest,
    ModelLaneReadEngineExitResult,
    ModelLaneReadLogTailRequest,
    ModelLaneReadLogTailResult,
    ModelLaneStartEngineRequest,
    ModelLaneStartEngineResult,
    ModelLaneStopEngineRequest,
    ModelLaneStopEngineResult,
)
from omnibase_spi.contracts.services.model_lane_process_runner_types import (
    ModelLaneProcessRunResult,
    ModelLaneProcessStartResult,
    ModelLaneStartSpec,
)

__all__ = [
    "ModelFloorTicketCreateRequest",
    "ModelFloorTicketCreateResult",
    "ModelFloorTicketLookupRequest",
    "ModelFloorTicketLookupResult",
    "ModelFloorTicketSearchRequest",
    "ModelFloorTicketSearchResult",
    "ModelLaneHostRef",
    "ModelLanePrepareWorktreeRequest",
    "ModelLanePrepareWorktreeResult",
    "ModelLaneReadEngineExitRequest",
    "ModelLaneReadEngineExitResult",
    "ModelLaneReadLogTailRequest",
    "ModelLaneReadLogTailResult",
    "ModelLaneStartEngineRequest",
    "ModelLaneStartEngineResult",
    "ModelLaneStopEngineRequest",
    "ModelLaneStopEngineResult",
    "ModelLaneProcessRunResult",
    "ModelLaneProcessStartResult",
    "ModelLaneStartSpec",
    "ModelLaneHostPoolReading",
    "ModelLaneHostPoolRequest",
    "ModelLaneHostPoolSnapshot",
    "ModelBranch",
    "ModelCheckRun",
    "ModelCIStatus",
    "ModelComment",
    "ModelDatabaseHealth",
    "ModelDiff",
    "ModelExecuteResult",
    "ModelHostCallAnswer",
    "ModelHostCallRequest",
    "ModelIssue",
    "ModelMergeResult",
    "ModelMigrationStatus",
    "ModelProject",
    "ModelPullRequest",
    "ModelQueryResult",
    "ModelTableInfo",
    "ModelLanePluginTree",
    "ModelLaneCloseoutCells",
    "ModelLaneShipPluginTreesResult",
    "ModelLaneStageInputRequest",
    "ModelLaneHostStepRequest",
    "ModelLaneShipPluginTreesRequest",
    "ModelLaneRunDirsResult",
    "ModelLaneChangeList",
    "ModelLaneLedgerOutboxRows",
    "ModelLaneRegistryRootResult",
    "ModelLaneStagedInput",
    "ModelLaneHostStepResult",
]
