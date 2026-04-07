# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ModelPullRequest -- wire-format contract for pull request data.

Returned by ProtocolCodeHost.get_pull_request() and list_pull_requests().

This module MUST NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ModelPullRequest(BaseModel):
    """Wire-format representation of a pull request from a code hosting platform.

    Attributes:
        number: PR number within the repository.
        title: PR title.
        body: PR description body (markdown).
        state: Current state (open, closed, merged).
        head_ref: Source branch name.
        base_ref: Target branch name.
        mergeable: Whether the PR can be cleanly merged. None if unknown.
        author: Username of the PR author.
        created_at: When the PR was created.
        updated_at: When the PR was last updated.
        merged_at: When the PR was merged. None if not merged.
        labels: Labels applied to the PR.
        review_decision: Review status (approved, changes_requested, review_required).
            None if no reviews.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    number: int = Field(
        ...,
        description="PR number within the repository.",
    )
    title: str = Field(
        ...,
        description="PR title.",
    )
    body: str = Field(
        default="",
        description="PR description body (markdown).",
    )
    state: str = Field(
        ...,
        description="Current state (open, closed, merged).",
    )
    head_ref: str = Field(
        ...,
        description="Source branch name.",
    )
    base_ref: str = Field(
        ...,
        description="Target branch name.",
    )
    mergeable: bool | None = Field(
        default=None,
        description="Whether the PR can be cleanly merged. None if unknown.",
    )
    author: str = Field(
        ...,
        description="Username of the PR author.",
    )
    created_at: datetime = Field(
        ...,
        description="When the PR was created.",
    )
    updated_at: datetime = Field(
        ...,
        description="When the PR was last updated.",
    )
    merged_at: datetime | None = Field(
        default=None,
        description="When the PR was merged. None if not merged.",
    )
    labels: list[str] = Field(
        default_factory=list,
        description="Labels applied to the PR.",
    )
    review_decision: str | None = Field(
        default=None,
        description="Review status (approved, changes_requested, review_required).",
    )
