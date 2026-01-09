"""Protocols for event-to-state projection and projector loading.

This module provides protocols for projectors that consume event streams
and materialize state to persistence stores.

Key Protocols:
    - ProtocolEventProjector: Event-to-state projection interface (OMN-1167)
    - ProtocolProjectorLoader: Loads projectors from YAML contracts

Architecture:
    Projectors are the bridge between event streams and queryable read models.
    They consume ModelEventEnvelope instances and materialize state that can
    be queried by orchestrators and services.

    Event Bus -> Projector -> Persistence Store -> Query Services

    The loader separates projector configuration from implementation:

    YAML Contract -> ProtocolProjectorLoader -> ProtocolEventProjector instance

Core Principle:
    Projectors are consumers only. They MUST NOT:
    - Emit events
    - Publish to event bus
    - Create intents
    - Have side effects beyond their target store

Note:
    ProtocolEventProjector (this module) handles event-to-state projection.
    ProtocolProjector in projections/ handles projection persistence with
    ordering guarantees. They serve different purposes:

    - ProtocolEventProjector: Consumes events, materializes state
    - projections.ProtocolProjector: Persists projections with ordering

Related:
    - projections.ProtocolProjector: Projection persistence with ordering
    - projections.ProtocolProjectionReader: Query interface for projections
    - event_bus.ProtocolEventEnvelope: Event envelope format
"""

from __future__ import annotations

from .protocol_event_projector import ProtocolEventProjector
from .protocol_projector_loader import ProtocolProjectorLoader

__all__ = [
    "ProtocolEventProjector",
    "ProtocolProjectorLoader",
]
