"""
Protocol interface for hybrid retrieval systems.

Defines the contract for retrieval systems that combine multiple search
strategies such as BM25 and dense vector search.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_semantic_types import (
        ProtocolRetrievalInputState,
        ProtocolRetrievalOutputState,
    )


@runtime_checkable
class ProtocolHybridRetriever(Protocol):
    """
    Protocol for hybrid retrieval tools.

    This protocol defines the interface for tools that combine multiple
    retrieval strategies to improve search relevance and coverage.
    """

    async def retrieve(
        self, input_state: "ProtocolRetrievalInputState"
    ) -> "ProtocolRetrievalOutputState":
        """
        Perform hybrid retrieval combining multiple search strategies.

        Args:
            input_state: Input state containing query and search parameters

        Returns:
            Output state with retrieved documents and metadata
        """
        ...
