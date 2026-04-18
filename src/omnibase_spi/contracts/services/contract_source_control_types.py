# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Wire-format models for source control service responses.

Frozen, data-only Pydantic models returned by ProtocolSourceControl
methods. No business logic, no SPI protocol references.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

_SCHEMA_VERSION = "1.0"


class ModelCheckRun(BaseModel):
    """A single CI check run result."""

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default=_SCHEMA_VERSION
    )  # string-version-ok: wire format
    name: str
    status: str
    conclusion: str | None = None
    url: str | None = None


class ModelCIStatus(BaseModel):
    """Aggregate CI status for a git ref."""

    model_config = {"frozen": True, "extra": "allow"}

    state: str
    checks: list[ModelCheckRun] = []


class ModelPullRequest(BaseModel):
    """Pull request data from a source control provider."""

    model_config = {"frozen": True, "extra": "allow"}

    number: int
    title: str
    state: str
    author: str
    head_ref: str
    base_ref: str
    mergeable: bool | None = None
    ci_status: str | None = None
    url: str
    created_at: datetime
    updated_at: datetime


class ModelMergeResult(BaseModel):
    """Result of a pull request merge operation."""

    model_config = {"frozen": True, "extra": "allow"}

    merged: bool
    sha: str | None = None
    message: str


class ModelBranch(BaseModel):
    """Git branch metadata."""

    model_config = {"frozen": True, "extra": "allow"}

    name: str
    sha: str
    protected: bool = False


class ModelDiff(BaseModel):
    """Diff summary between two git refs."""

    model_config = {"frozen": True, "extra": "allow"}

    files_changed: int
    additions: int
    deletions: int
    patch: str = ""
