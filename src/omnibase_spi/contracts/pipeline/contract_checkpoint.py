"""ContractCheckpoint -- phase checkpoint wire format.

Represents a snapshot of pipeline state at the boundary between phases,
enabling crash recovery and resume-from-checkpoint behavior.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ContractCheckpoint(BaseModel):
    """Phase checkpoint for pipeline resume support.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        run_id: Correlation ID for the pipeline run.
        phase: Phase name this checkpoint represents.
        status: Status of the phase at checkpoint time.
        created_at_iso: ISO-8601 timestamp when the checkpoint was created.
        artifacts: Named artifacts produced up to this point.
        metadata: Arbitrary metadata for checkpoint context.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    run_id: str = Field(
        ...,
        description="Correlation ID for the pipeline run.",
    )
    phase: str = Field(
        ...,
        description="Phase name this checkpoint represents.",
    )
    status: Literal["completed", "in_progress", "failed", "blocked"] = Field(
        ...,
        description="Status of the phase at checkpoint time.",
    )
    created_at_iso: str = Field(
        default="",
        description="ISO-8601 timestamp when the checkpoint was created.",
    )
    artifacts: dict[str, Any] = Field(
        default_factory=dict,
        description="Named artifacts produced up to this point.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata for checkpoint context.",
    )
