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

__all__ = [
    "ModelBranch",
    "ModelCheckRun",
    "ModelCIStatus",
    "ModelComment",
    "ModelDatabaseHealth",
    "ModelDiff",
    "ModelExecuteResult",
    "ModelIssue",
    "ModelMergeResult",
    "ModelMigrationStatus",
    "ModelProject",
    "ModelPullRequest",
    "ModelQueryResult",
    "ModelTableInfo",
]
