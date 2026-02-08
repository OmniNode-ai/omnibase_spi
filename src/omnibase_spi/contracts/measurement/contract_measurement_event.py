"""ContractMeasurementEvent -- domain wrapper for measurement data.

Wraps a ``ContractPhaseMetrics`` payload with event-level metadata
(event_id, timestamp, event_type).  This is a *domain* envelope, NOT a
transport envelope -- transport framing is handled by the event bus.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from omnibase_spi.contracts.measurement.contract_phase_metrics import (
    ContractPhaseMetrics,
)


class ContractMeasurementEvent(BaseModel):
    """Domain envelope for a measurement event.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        event_id: Unique identifier for this event.
        event_type: Event type discriminator (e.g. 'phase_completed').
        timestamp_iso: ISO-8601 timestamp when the event was produced.
        payload: The measurement data.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    event_id: str = Field(
        ...,
        description="Unique identifier for this event.",
    )
    event_type: str = Field(
        default="phase_completed",
        description="Event type discriminator (e.g. 'phase_completed').",
    )
    timestamp_iso: str = Field(
        default="",
        description="ISO-8601 timestamp when the event was produced.",
    )
    payload: ContractPhaseMetrics = Field(
        ...,
        description="The measurement data.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )
