# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Source control wire-format contracts for ProtocolCodeHost return types."""

from omnibase_spi.contracts.source_control.model_branch import ModelBranch
from omnibase_spi.contracts.source_control.model_check_run import ModelCheckRun
from omnibase_spi.contracts.source_control.model_diff import ModelDiff
from omnibase_spi.contracts.source_control.model_merge_result import ModelMergeResult
from omnibase_spi.contracts.source_control.model_pull_request import ModelPullRequest

__all__ = [
    "ModelBranch",
    "ModelCheckRun",
    "ModelDiff",
    "ModelMergeResult",
    "ModelPullRequest",
]
