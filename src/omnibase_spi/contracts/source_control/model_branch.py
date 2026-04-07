# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ModelBranch -- wire-format contract for branch data.

Returned by ProtocolCodeHost branch operations.

This module MUST NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModelBranch(BaseModel):
    """Wire-format representation of a git branch.

    Attributes:
        name: Branch name (e.g. "main", "feature/foo").
        sha: Commit SHA at the branch tip.
        protected: Whether the branch has protection rules enabled.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    name: str = Field(
        ...,
        description="Branch name.",
    )
    sha: str = Field(
        ...,
        description="Commit SHA at the branch tip.",
    )
    protected: bool = Field(
        default=False,
        description="Whether the branch has protection rules enabled.",
    )
