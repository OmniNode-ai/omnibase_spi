# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ModelCheckRun -- wire-format contract for CI check run data.

Returned by ProtocolCodeHost CI status operations.

This module MUST NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ModelCheckRun(BaseModel):
    """Wire-format representation of a CI check run.

    Attributes:
        name: Check run name (e.g. "lint", "test", "build").
        status: Execution status (queued, in_progress, completed).
        conclusion: Outcome when completed (success, failure, neutral, cancelled,
            skipped, timed_out, action_required). None while in progress.
        started_at: When the check run started. None if queued.
        completed_at: When the check run finished. None if not completed.
        details_url: URL to the full check run details. None if unavailable.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    name: str = Field(
        ...,
        description="Check run name.",
    )
    status: str = Field(
        ...,
        description="Execution status (queued, in_progress, completed).",
    )
    conclusion: str | None = Field(
        default=None,
        description="Outcome when completed. None while in progress.",
    )
    started_at: datetime | None = Field(
        default=None,
        description="When the check run started. None if queued.",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the check run finished. None if not completed.",
    )
    details_url: str | None = Field(
        default=None,
        description="URL to the full check run details.",
    )
