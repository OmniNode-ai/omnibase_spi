"""ContractProducer -- structured producer identity.

Identifies the producer of a measurement: which tool or agent, at what
version, and with what instance identity produced the data.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ContractProducer(BaseModel):
    """Structured identity for a measurement producer.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        name: Producer name (e.g. 'ticket-pipeline', 'pytest').
        version: Producer version string.
        instance_id: Unique instance identifier for this producer run.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    name: str = Field(
        ...,
        description="Producer name (e.g. 'ticket-pipeline', 'pytest').",
    )
    version: str = Field(
        default="",
        description="Producer version string.",
    )
    instance_id: str = Field(
        default="",
        description="Unique instance identifier for this producer run.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )
