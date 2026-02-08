"""ContractRunContext -- per-run state wire format.

Captures the mutable state that flows through a single pipeline run and
is persisted between phases for resume support.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContractRunContext(BaseModel):
    """Per-run state carried through a pipeline execution.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        run_id: Unique identifier for this pipeline run.
        session_id: Stable session identifier across runs.
        ticket_id: Associated ticket (e.g. OMN-1234).
        repo: Repository name or path.
        branch: Git branch name.
        phase: Current pipeline phase name.
        attempt: Retry attempt number for the current phase.
        env: Environment key-value pairs available to nodes.
        artifacts: Named artifact references produced so far.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    run_id: str = Field(
        ...,
        description="Unique identifier for this pipeline run.",
    )
    session_id: str = Field(
        default="",
        description="Stable session identifier across runs.",
    )
    ticket_id: str = Field(
        default="",
        description="Associated ticket (e.g. OMN-1234).",
    )
    repo: str = Field(
        default="",
        description="Repository name or path.",
    )
    branch: str = Field(
        default="",
        description="Git branch name.",
    )
    phase: str = Field(
        default="",
        description="Current pipeline phase name.",
    )
    attempt: int = Field(
        default=1,
        ge=1,
        description="Retry attempt number for the current phase.",
    )
    env: dict[str, str] = Field(
        default_factory=dict,
        description="Environment key-value pairs available to nodes.",
    )
    artifacts: dict[str, Any] = Field(
        default_factory=dict,
        description="Named artifact references produced so far.",
    )
