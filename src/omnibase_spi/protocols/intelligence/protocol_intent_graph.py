# SPDX-License-Identifier: MIT
# Copyright (c) 2025 OmniNode Team
"""Protocol for intent graph persistence operations.

This module defines the protocol for storing and retrieving intent classification
results. Implementations provide persistence abstraction, allowing omniintelligence
to remain memory-agnostic while supporting optional intent storage.

The intent graph tracks:
- Session-scoped intent history
- Intent classification results with confidence scores
- Correlation IDs for distributed tracing

Note:
    This protocol references types from omnibase_core.models.events that will be
    created as part of OMN-1479 implementation:
    - IntentRecordPayload: Payload for stored intent records
    - ModelIntentStoredEvent: Event emitted when an intent is stored

Example:
    >>> class MyIntentGraph:
    ...     async def store_intent(
    ...         self,
    ...         session_id: str,
    ...         intent_data: ModelIntentClassificationInput,
    ...         correlation_id: str | None = None,
    ...     ) -> ModelIntentStoredEvent:
    ...         # Implementation here
    ...         ...
    >>>
    >>> # Check protocol compliance
    >>> assert isinstance(MyIntentGraph(), ProtocolIntentGraph)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.events import IntentRecordPayload, ModelIntentStoredEvent
    from omnibase_core.models.intelligence import ModelIntentClassificationInput

__all__ = ["ProtocolIntentGraph"]


@runtime_checkable
class ProtocolIntentGraph(Protocol):
    """Protocol for intent graph persistence operations.

    Defines the interface for storing and retrieving intent classification
    results. This abstraction allows the intelligence layer to optionally
    persist intent data without coupling to specific storage implementations.

    Use cases:
    - Session history tracking for context-aware responses
    - Intent pattern analysis across sessions
    - Debugging and observability of classification decisions
    - Replay and audit capabilities

    Example:
        >>> async def example():
        ...     graph: ProtocolIntentGraph = get_intent_graph()
        ...     # Store a new intent
        ...     event = await graph.store_intent(session_id, intent_data)
        ...     # Retrieve session intents
        ...     intents = await graph.get_session_intents(session_id, min_confidence=0.7)
        ...     print(f"Found {len(intents)} high-confidence intents")
    """

    async def store_intent(
        self,
        session_id: str,
        intent_data: ModelIntentClassificationInput,
        correlation_id: str | None = None,
    ) -> ModelIntentStoredEvent:
        """Store an intent classification result in the graph.

        Persists the intent data associated with a session for later retrieval.
        The correlation_id enables distributed tracing across service boundaries.

        Args:
            session_id: Unique identifier for the session. Used to group related
                intents together for retrieval.
            intent_data: The intent classification input containing content,
                context, and optional correlation metadata.
            correlation_id: Optional identifier for distributed tracing. If not
                provided, implementations may generate one.

        Returns:
            Event confirming the intent was stored, containing:
                - event_id: Unique identifier for this storage event
                - session_id: The session the intent was stored under
                - timestamp: When the intent was stored
                - correlation_id: Tracing identifier (provided or generated)

        Raises:
            May raise implementation-specific exceptions for storage failures,
            invalid session IDs, or serialization errors.
        """
        ...

    async def get_session_intents(
        self,
        session_id: str,
        min_confidence: float = 0.0,
        limit: int | None = None,
    ) -> list[IntentRecordPayload]:
        """Retrieve stored intents for a session.

        Fetches intent records matching the session ID with optional filtering
        by confidence threshold and result limiting.

        Args:
            session_id: Unique identifier for the session to query.
            min_confidence: Minimum confidence threshold (0.0 to 1.0). Only
                intents with confidence >= this value are returned. Defaults
                to 0.0 (no filtering).
            limit: Maximum number of intents to return. If None, returns all
                matching intents. Results are typically ordered by timestamp
                (most recent first).

        Returns:
            List of intent records matching the criteria. Each record contains:
                - intent_category: The classified intent type
                - confidence: Classification confidence score
                - timestamp: When the intent was classified
                - content_hash: Hash of the original content (for deduplication)
                - metadata: Additional classification metadata

        Raises:
            May raise implementation-specific exceptions for invalid session IDs,
            query failures, or deserialization errors.
        """
        ...

    async def health_check(self) -> bool:
        """Check if the intent graph storage is healthy and accessible.

        Performs a lightweight check to verify the underlying storage
        is reachable and operational. Used for service health monitoring
        and circuit breaker patterns.

        Returns:
            True if the storage is healthy and accessible, False otherwise.
            Implementations should not raise exceptions; connection or
            operational issues should result in False.

        Example:
            >>> async def monitor():
            ...     graph: ProtocolIntentGraph = get_intent_graph()
            ...     if not await graph.health_check():
            ...         logger.warning("Intent graph storage unavailable")
        """
        ...
