"""ContractHookInvocation -- outer envelope (shell shim -> adapter).

Represents the request sent from the shell shim to the hook adapter when a
Claude Code hook fires.  The adapter unpacks this into a
:class:`ContractNodeOperationRequest` before dispatching to a node.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContractHookInvocation(BaseModel):
    """Outer envelope sent from shell shim to hook adapter.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        hook_name: Name of the hook that fired (e.g. PreToolUse, PostToolUse).
        tool_name: Name of the tool being invoked.
        tool_input: Raw tool input as received from the hook.
        session_id: Stable session identifier.
        run_id: Correlation ID for this pipeline run.
        timestamp_iso: ISO-8601 timestamp of invocation.
        metadata: Arbitrary key-value metadata from the shell environment.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    hook_name: str = Field(
        ...,
        description="Name of the hook that fired (e.g. PreToolUse).",
    )
    tool_name: str = Field(
        ...,
        description="Name of the tool being invoked.",
    )
    tool_input: dict[str, Any] = Field(
        default_factory=dict,
        description="Raw tool input as received from the hook.",
    )
    session_id: str = Field(
        default="",
        description="Stable session identifier.",
    )
    run_id: str = Field(
        default="",
        description="Correlation ID for this pipeline run.",
    )
    timestamp_iso: str = Field(
        default="",
        description="ISO-8601 timestamp of invocation.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary key-value metadata from the shell environment.",
    )
