"""ContractHookInvocationResult -- outer response (adapter -> shell shim).

Represents the response the hook adapter sends back to the shell shim after
processing a :class:`ContractHookInvocation`.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from omnibase_spi.contracts.pipeline.contract_node_error import ContractNodeError


class ContractHookInvocationResult(BaseModel):
    """Outer response from hook adapter back to shell shim.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        decision: Whether to allow, block, or modify the tool invocation.
        reason: Human-readable explanation of the decision.
        modified_input: If decision is 'modify', the replacement tool input.
        errors: Structured errors encountered during processing.
        duration_ms: Wall-clock time for the entire hook processing.
        metadata: Arbitrary key-value metadata for the shell environment.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    decision: Literal["allow", "block", "modify"] = Field(
        default="allow",
        description="Whether to allow, block, or modify the tool invocation.",
    )
    reason: str = Field(
        default="",
        description="Human-readable explanation of the decision.",
    )
    modified_input: dict[str, Any] | None = Field(
        default=None,
        description="If decision is 'modify', the replacement tool input.",
    )
    errors: list[ContractNodeError] = Field(
        default_factory=list,
        description="Structured errors encountered during processing.",
    )
    duration_ms: float | None = Field(
        default=None,
        description="Wall-clock time for the entire hook processing.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary key-value metadata for the shell environment.",
    )
