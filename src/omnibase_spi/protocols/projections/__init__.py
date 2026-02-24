"""Protocols for projection persistence, state reading, and view dispatch.

This module provides protocols for the projection layer:
- Persistence: Projector writes projections with ordering guarantees
- Reading: Reader queries materialized projection state
- View Dispatch: ProtocolProjectionView for NodeProjectionEffect registry pattern

Key Protocols:
    - ProtocolProjector: Persists projections with ordering enforcement
    - ProtocolProjectionReader: Queries materialized projection state
    - ProtocolSequenceInfo: Sequence information for ordering
    - ProtocolPersistResult: Result of persist operations
    - ProtocolBatchPersistResult: Result of batch persist operations
    - ProtocolProjectionView: Simplified synchronous SPI for view implementations
        registered in NodeProjectionEffect (OMN-2382)

Protocol Distinction:
    - ProtocolProjector: Async, handles persistence with sequence ordering.
      Takes (projection, entity_id, domain, sequence_info). Production persistence layer.
    - ProtocolProjectionView: Synchronous, takes ModelProjectionIntent, returns
      ContractProjectionResult. Used by NodeProjectionEffect registry pattern.
    - ProtocolEventProjector (projectors/): Async, takes ModelEnvelope, materializes
      state. Focus on event-to-state projection semantics.

Architecture:
    Projections flow from reducers through the projector to persistence,
    and are later queried by orchestrators through the projection reader:

    Reducer -> Runtime -> Projector -> Database <- ProjectionReader <- Orchestrator

    NodeProjectionEffect registry pattern (OMN-2382):

    Reducer -> ModelProjectionIntent -> NodeProjectionEffect
            -> ProtocolProjectionView.project_intent() -> ContractProjectionResult

    The projector enforces:
    1. Per-entity monotonic ordering (sequence must increase)
    2. Idempotent writes (duplicate sequences rejected)
    3. Concurrent write safety (atomic check-and-persist)

CRITICAL ARCHITECTURAL CONSTRAINT:
    Orchestrators MUST NEVER scan Kafka/event topics directly for state.
    All orchestration decisions MUST be projection-backed through these protocols.

Related:
    - ProtocolIdempotencyStore: Runtime-level message deduplication (B3)
    - ProtocolReducerNode: Produces projections from events
    - NodeProjectionEffect: Concrete generic effect node (omnibase_spi.effects)
"""

from __future__ import annotations

from .protocol_projection_reader import ProtocolProjectionReader
from .protocol_projection_view import ProtocolProjectionView
from .protocol_projector import (
    ProtocolBatchPersistResult,
    ProtocolPersistResult,
    ProtocolProjector,
    ProtocolSequenceInfo,
)

__all__ = [
    "ProtocolBatchPersistResult",
    "ProtocolPersistResult",
    "ProtocolProjectionReader",
    "ProtocolProjectionView",
    "ProtocolProjector",
    "ProtocolSequenceInfo",
]
