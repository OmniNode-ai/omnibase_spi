"""ContractAuthGateInput -- auth decision input.

Captures the information needed by the authorization gate to decide
whether to allow, deny, or escalate an operation.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContractAuthGateInput(BaseModel):
    """Input to the authorization gate for a pipeline operation.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        run_id: Correlation ID for the pipeline run.
        session_id: Stable session identifier.
        tool_name: Name of the tool requesting authorization.
        hook_name: Hook that triggered the auth check.
        operation: Specific operation being authorized.
        resource: Resource being accessed (file path, URL, etc.).
        agent_id: Identifier of the agent requesting authorization.
        context: Additional context for the authorization decision.
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
    tool_name: str = Field(
        default="",
        description="Name of the tool requesting authorization.",
    )
    hook_name: str = Field(
        default="",
        description="Hook that triggered the auth check.",
    )
    operation: str = Field(
        default="",
        description="Specific operation being authorized.",
    )
    resource: str = Field(
        default="",
        description="Resource being accessed (file path, URL, etc.).",
    )
    agent_id: str = Field(
        default="",
        description="Identifier of the agent requesting authorization.",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the authorization decision.",
    )
