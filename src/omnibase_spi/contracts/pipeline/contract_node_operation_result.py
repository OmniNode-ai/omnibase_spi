"""ContractNodeOperationResult -- inner response (node -> adapter).

Represents the response an ONEX node sends back to the adapter after
executing a :class:`ContractNodeOperationRequest`.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from omnibase_spi.contracts.pipeline.contract_node_error import ContractNodeError


class ContractNodeOperationResult(BaseModel):
    """Inner response from an ONEX node back to the adapter.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        node_id: Node that produced this result.
        status: Outcome of the operation.
        output: Operation-specific output payload.
        errors: Structured errors if status is 'error'.
        duration_ms: Wall-clock time for the node operation.
        metadata: Arbitrary key-value metadata from the node.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    node_id: str = Field(
        default="",
        description="Node that produced this result.",
    )
    status: Literal["success", "error", "skipped"] = Field(
        ...,
        description="Outcome of the operation.",
    )
    output: dict[str, Any] = Field(
        default_factory=dict,
        description="Operation-specific output payload.",
    )
    errors: list[ContractNodeError] = Field(
        default_factory=list,
        description="Structured errors if status is 'error'.",
    )
    duration_ms: float | None = Field(
        default=None,
        description="Wall-clock time for the node operation.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary key-value metadata from the node.",
    )
