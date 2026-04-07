# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ModelMergeResult -- wire-format contract for merge outcome data.

Returned by ProtocolCodeHost.merge_pull_request().

This module MUST NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModelMergeResult(BaseModel):
    """Wire-format representation of a pull request merge outcome.

    Attributes:
        merged: Whether the merge was successful.
        sha: Commit SHA of the merge commit. None if merge failed.
        message: Human-readable merge status message.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    merged: bool = Field(
        ...,
        description="Whether the merge was successful.",
    )
    sha: str | None = Field(
        default=None,
        description="Commit SHA of the merge commit. None if merge failed.",
    )
    message: str = Field(
        default="",
        description="Human-readable merge status message.",
    )
