# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ContractPrValidationRollup -- PR-level validation tax rollup.

Captures the validation overhead (reruns, failures, escalations) for a
single PR run, enabling Validation Tax Score (VTS) computation and
cross-model efficiency comparison.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ContractValidationTax(BaseModel):
    """Raw validation tax counters for a single PR run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    blocking_failures: int = Field(
        default=0,
        description="Number of blocking validation failures.",
    )
    warn_findings: int = Field(
        default=0,
        description="Number of warning-level validation findings.",
    )
    reruns: int = Field(
        default=0,
        description="Number of pipeline reruns triggered by failures.",
    )
    validator_runtime_ms: int = Field(
        default=0,
        description="Total validator wall-clock time in milliseconds.",
    )
    human_escalations: int = Field(
        default=0,
        description="Number of times a human had to intervene.",
    )
    autofix_successes: int = Field(
        default=0,
        description="Number of issues automatically fixed (reduces VTS).",
    )
    time_to_green_ms: int = Field(
        default=0,
        description="Wall-clock time from first run to green in milliseconds.",
    )


class ContractPrScope(BaseModel):
    """Scope metadata for a PR (size indicators)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    files_changed: int = Field(
        default=0,
        description="Number of files changed in the PR.",
    )
    lines_changed: int = Field(
        default=0,
        description="Total lines changed (added + removed).",
    )
    module_tags: list[str] = Field(
        default_factory=list,
        description="Module or area tags for the changed code.",
    )


class ContractPrValidationRollup(BaseModel):
    """PR-level validation rollup for VTS computation.

    Frozen, high-integrity wire-format contract that captures
    all validation tax data for a single PR run.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    metric_version: str = Field(
        default="v1",
        description="VTS metric formula version.",
    )
    repo_id: str = Field(
        ...,
        description="Repository identifier.",
    )
    pr_id: str = Field(
        default="",
        description="Pull request identifier.",
    )
    pr_url: str = Field(
        default="",
        description="Pull request URL.",
    )
    run_id: str = Field(
        ...,
        description="Unique run identifier.",
    )
    ticket_id: str = Field(
        default="",
        description="Associated ticket identifier.",
    )
    model_id: str = Field(
        ...,
        description="LLM model identifier that produced the measured work.",
    )
    producer_kind: Literal["agent", "human", "unknown"] = Field(
        default="unknown",
        description="Producer type. Constrained to prevent free-string drift.",
    )
    rollup_status: Literal["final", "partial"] = Field(
        default="final",
        description="Whether this rollup is final or partial (in-progress).",
    )
    scope: ContractPrScope = Field(
        default_factory=ContractPrScope,
        description="PR scope metadata.",
    )
    tax: ContractValidationTax = Field(
        default_factory=ContractValidationTax,
        description="Raw validation tax counters.",
    )
    vts: float = Field(
        default=0.0,
        description="Computed Validation Tax Score.",
    )
    vts_per_kloc: float = Field(
        default=0.0,
        description="VTS normalised per 1000 lines changed.",
    )
    phase_count: int = Field(
        default=0,
        description="Number of pipeline phases executed.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )
