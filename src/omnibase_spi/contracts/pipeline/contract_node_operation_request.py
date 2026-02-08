"""ContractNodeOperationRequest -- inner envelope (adapter -> node).

Represents the request the adapter dispatches to an ONEX node after
unpacking a :class:`ContractHookInvocation`.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContractNodeOperationRequest(BaseModel):
    """Inner envelope dispatched from adapter to an ONEX node.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        node_id: Target node identifier.
        operation: Operation to execute on the node.
        parameters: Operation-specific parameters.
        run_id: Correlation ID carried from the outer invocation.
        session_id: Stable session identifier.
        timeout_ms: Maximum allowed execution time in milliseconds.
        metadata: Arbitrary key-value metadata forwarded to the node.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    node_id: str = Field(
        ...,
        description="Target node identifier.",
    )
    operation: str = Field(
        ...,
        description="Operation to execute on the node.",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Operation-specific parameters.",
    )
    run_id: str = Field(
        default="",
        description="Correlation ID carried from the outer invocation.",
    )
    session_id: str = Field(
        default="",
        description="Stable session identifier.",
    )
    timeout_ms: int | None = Field(
        default=None,
        description="Maximum allowed execution time in milliseconds.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary key-value metadata forwarded to the node.",
    )
