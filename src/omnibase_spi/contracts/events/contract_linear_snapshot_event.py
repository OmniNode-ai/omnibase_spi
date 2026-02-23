"""ContractLinearSnapshotEvent — SPI wire contract for Linear snapshot events.

Topic: ``onex.evt.linear.snapshot.v1``
Partition key: ``snapshot_id``

This contract captures a point-in-time snapshot of Linear workstreams as
polled by ``ProtocolLinearSnapshotEffect``.  It is the SPI-layer view: a
strict subset of ``ModelLinearSnapshotEvent`` from omnibase_core.

Design constraints:
    - ``extra="forbid"``: no undeclared fields permitted.
    - ``frozen=True``: instances are immutable after construction.
    - ``snapshot_id`` is the partition key; it must be stable and globally
      unique (UUID4 or similar).
    - ``workstreams`` is a list of workstream identifier strings sourced
      from the Linear workspace.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContractLinearSnapshotEvent(BaseModel):
    """SPI wire contract for a Linear snapshot event.

    Published to ``onex.evt.linear.snapshot.v1`` by
    ``ProtocolLinearSnapshotEffect`` after polling the Linear workspace.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        event_type: Must equal ``"onex.evt.linear.snapshot.v1"``.
        snapshot_id: Globally-unique identifier for this snapshot (used as
            the Kafka partition key).
        workstreams: List of Linear workstream identifiers captured in
            this snapshot.
        extensions: Single extension channel for consumer-specific metadata.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    event_type: str = Field(
        default="onex.evt.linear.snapshot.v1",
        description="Fully-qualified event type identifier; equals the topic name.",
    )
    snapshot_id: str = Field(
        ...,
        description=(
            "Globally-unique snapshot identifier (UUID4 recommended). "
            "Used as the Kafka partition key."
        ),
    )
    workstreams: list[str] = Field(
        default_factory=list,
        description="Linear workstream identifiers captured in this snapshot.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Single extension channel for consumer-specific metadata. "
            "Domain fields MUST NOT be embedded here."
        ),
    )
