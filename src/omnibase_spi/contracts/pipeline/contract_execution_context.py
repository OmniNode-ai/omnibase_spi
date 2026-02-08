"""ContractExecutionContext -- active skill/command state.

Captures the active execution context when a skill or command is running,
including what tool is active, what permissions were granted, and the
current pipeline phase.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContractExecutionContext(BaseModel):
    """Active skill or command execution state.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        run_id: Correlation ID for the pipeline run.
        session_id: Stable session identifier.
        skill_name: Name of the active skill (empty if raw command).
        command_name: Name of the active command.
        hook_name: Hook that triggered this execution (if any).
        phase: Current pipeline phase.
        tool_name: Active tool name.
        permissions: Granted permission scopes for this execution.
        env: Environment variables available to the execution.
        metadata: Arbitrary metadata for the execution.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    run_id: str = Field(
        default="",
        description="Correlation ID for the pipeline run.",
    )
    session_id: str = Field(
        default="",
        description="Stable session identifier.",
    )
    skill_name: str = Field(
        default="",
        description="Name of the active skill (empty if raw command).",
    )
    command_name: str = Field(
        default="",
        description="Name of the active command.",
    )
    hook_name: str = Field(
        default="",
        description="Hook that triggered this execution (if any).",
    )
    phase: str = Field(
        default="",
        description="Current pipeline phase.",
    )
    tool_name: str = Field(
        default="",
        description="Active tool name.",
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Granted permission scopes for this execution.",
    )
    env: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables available to the execution.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata for the execution.",
    )
