# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Wire-format models for project tracker service responses.

Frozen, data-only Pydantic models returned by ProtocolProjectTracker
methods. No business logic, no SPI protocol references.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

_SCHEMA_VERSION = "1.0"


class ModelComment(BaseModel):
    """A comment on an issue or ticket."""

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(default=_SCHEMA_VERSION)
    id: str
    body: str
    author: str
    created_at: datetime


class ModelIssue(BaseModel):
    """Issue/ticket data from a project tracker.

    ``identifier`` is the human-readable ticket ID (e.g. "OMN-1234"),
    ``id`` is the internal UUID used by the provider.
    """

    model_config = {"frozen": True, "extra": "allow"}

    id: str
    identifier: str
    title: str
    description: str | None = None
    state: str
    priority: str | None = None
    assignee: str | None = None
    labels: list[str] = []
    team: str | None = None
    project_id: str | None = None
    url: str | None = None
    created_at: datetime
    updated_at: datetime


class ModelProject(BaseModel):
    """Project or workspace data from a project tracker."""

    model_config = {"frozen": True, "extra": "allow"}

    id: str
    name: str
    description: str | None = None
    state: str | None = None
    progress: float = 0.0
    url: str | None = None
