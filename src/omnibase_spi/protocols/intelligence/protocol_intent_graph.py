"""Protocol for intent graph persistence operations.

This module defines the protocol for storing and retrieving intent classifications
from a graph database. Implementations handle the actual storage mechanism
(e.g., Memgraph, Neo4j) while consumers depend only on this protocol.

This protocol enables dependency inversion - intelligence services can
use intent persistence without knowing the storage implementation.

Example:
    >>> class MyIntentGraph:
    ...     async def store_intent(
    ...         self,
    ...         session_id: str,
    ...         intent_data: ModelIntentClassificationInput,
    ...         correlation_id: str,
    ...     ) -> ModelIntentStorageResult:
    ...         # Implementation here
    ...         ...
    >>>
    >>> # Check protocol compliance
    >>> assert isinstance(MyIntentGraph(), ProtocolIntentGraph)

See Also:
    ModelIntentClassificationInput: Input data for intent storage.
    ModelIntentStorageResult: Result of storage operations.
    ModelIntentQueryResult: Result of query operations.
    OMN-1457: AdapterIntentGraph implementation in omnimemory.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.intelligence import (
        ModelIntentClassificationInput,
        ModelIntentQueryResult,
        ModelIntentStorageResult,
    )

__all__ = ["ProtocolIntentGraph"]


@runtime_checkable
class ProtocolIntentGraph(Protocol):
    """Protocol for intent graph persistence operations.

    Defines the capability for storing and retrieving intent classifications
    from a graph database. Implementations handle the actual storage mechanism
    (e.g., Memgraph, Neo4j) while consumers depend only on this protocol.

    This protocol enables dependency inversion - intelligence services can
    use intent persistence without knowing the storage implementation.

    Example:
        ```python
        graph: ProtocolIntentGraph = get_intent_graph()

        # Store an intent
        result = await graph.store_intent(
            session_id="session-123",
            intent_data=classification_input,
            correlation_id="corr-456",
        )

        # Query intents
        intents = await graph.get_session_intents(
            session_id="session-123",
            min_confidence=0.7,
        )
        ```

    See Also:
        ModelIntentClassificationInput: Input data for intent storage.
        ModelIntentStorageResult: Result of storage operations.
        ModelIntentQueryResult: Result of query operations.
        OMN-1457: AdapterIntentGraph implementation in omnimemory.
    """

    async def store_intent(
        self,
        session_id: str,
        intent_data: ModelIntentClassificationInput,
        correlation_id: str,
    ) -> ModelIntentStorageResult:
        """Store an intent classification in the graph.

        Args:
            session_id: Unique identifier for the user session.
            intent_data: The classified intent data to store.
            correlation_id: Correlation ID for tracing.

        Returns:
            Storage result indicating success/failure and the intent ID.
        """
        ...

    async def get_session_intents(
        self,
        session_id: str,
        min_confidence: float = 0.0,
        limit: int | None = None,
    ) -> ModelIntentQueryResult:
        """Retrieve intents for a session.

        Args:
            session_id: The session to query intents for.
            min_confidence: Minimum confidence threshold (0.0 to 1.0).
            limit: Maximum number of intents to return, or None for all.

        Returns:
            Query result containing matching intent records.
        """
        ...

    async def health_check(self) -> bool:
        """Check if the intent graph storage is healthy and accessible.

        Returns:
            True if the storage is healthy, False otherwise.
        """
        ...
