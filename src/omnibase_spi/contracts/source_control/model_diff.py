# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ModelDiff -- wire-format contract for diff data.

Returned by ProtocolCodeHost diff operations.

This module MUST NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModelDiff(BaseModel):
    """Wire-format representation of a code diff between two refs.

    Attributes:
        files_changed: Number of files changed in the diff.
        additions: Total lines added.
        deletions: Total lines deleted.
        patch: Unified diff patch text. Empty string if not requested.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    files_changed: int = Field(
        ...,
        description="Number of files changed in the diff.",
    )
    additions: int = Field(
        ...,
        description="Total lines added.",
    )
    deletions: int = Field(
        ...,
        description="Total lines deleted.",
    )
    patch: str = Field(
        default="",
        description="Unified diff patch text. Empty string if not requested.",
    )
