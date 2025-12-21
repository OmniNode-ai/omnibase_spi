"""Protocols for projection persistence and state reading.

This module provides protocols for the projection layer:
- Persistence: Projector writes projections with ordering guarantees
- Reading: Reader queries materialized projection state

Key Protocols:
    - ProtocolProjector: Persists projections with ordering enforcement
    - ProtocolProjectionReader: Queries materialized projection state
    - ProtocolSequenceInfo: Sequence information for ordering
    - ProtocolPersistResult: Result of persist operations
    - ProtocolBatchPersistResult: Result of batch persist operations

Architecture:
    Projections flow from reducers through the projector to persistence,
    and are later queried by orchestrators through the projection reader:

    Reducer -> Runtime -> Projector -> Database <- ProjectionReader <- Orchestrator

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
"""

from __future__ import annotations

from .protocol_projection_reader import ProtocolProjectionReader
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
    "ProtocolProjector",
    "ProtocolSequenceInfo",
]
