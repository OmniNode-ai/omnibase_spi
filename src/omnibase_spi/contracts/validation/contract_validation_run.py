"""ContractValidationRun -- single validation execution.

Captures the metadata of a single execution of a validation plan,
including timing and correlation information.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ContractValidationRun(BaseModel):
    """Metadata for a single validation plan execution.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        run_id: Unique identifier for this validation run.
        plan_id: Validation plan that was executed.
        status: Current status of the run.
        started_at_iso: ISO-8601 timestamp when the run started.
        completed_at_iso: ISO-8601 timestamp when the run completed.
        duration_ms: Wall-clock time for the entire run.
        executor: Identifier of the executor (agent, CI system, etc.).
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    run_id: str = Field(
        ...,
        description="Unique identifier for this validation run.",
    )
    plan_id: str = Field(
        default="",
        description="Validation plan that was executed.",
    )
    status: Literal["pending", "running", "completed", "failed"] = Field(
        default="pending",
        description="Current status of the run.",
    )
    started_at_iso: str = Field(
        default="",
        description="ISO-8601 timestamp when the run started.",
    )
    completed_at_iso: str = Field(
        default="",
        description="ISO-8601 timestamp when the run completed.",
    )
    duration_ms: float | None = Field(
        default=None,
        description="Wall-clock time for the entire run.",
    )
    executor: str = Field(
        default="",
        description="Identifier of the executor (agent, CI system, etc.).",
    )
