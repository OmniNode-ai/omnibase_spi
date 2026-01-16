"""
Protocol interface for multi-vector indexing implementations.

Defines the contract for tools that implement DPR-style multi-vector
document indexing with passage-level granularity and document context.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType
    from omnibase_spi.protocols.types.protocol_advanced_types import (
        ProtocolInputDocument,
        ProtocolMultiVectorDocument,
    )


@runtime_checkable
class ProtocolMultiVectorIndexer(Protocol):
    """
    Protocol for DPR-style multi-vector document indexing with passage-level granularity.

    Defines the contract for multi-vector indexing implementations that segment documents
    into passages, generate embeddings for each passage, and maintain document-level
    context. Enables dense passage retrieval workflows with semantic search capabilities.

    Example:
        ```python
        from omnibase_spi.protocols.advanced import ProtocolMultiVectorIndexer
        from omnibase_spi.protocols.types import ProtocolInputDocument

        async def index_knowledge_base(
            indexer: ProtocolMultiVectorIndexer,
            documents: list[ProtocolInputDocument]
        ) -> list["ProtocolMultiVectorDocument"]:
            # Batch index documents with passage embeddings
            indexed_docs = await indexer.index_documents(documents)

            print(f"Indexed {len(indexed_docs)} documents")
            for doc in indexed_docs:
                print(f"  - {doc.document_id}: {len(doc.passages)} passages")

            # Get indexing statistics
            stats = await indexer.get_index_statistics()
            print(f"Total passages: {stats.get('total_passages')}")
            print(f"Average passages per doc: {stats.get('avg_passages_per_doc')}")

            return indexed_docs
        ```

    Key Features:
        - DPR-style passage-level embedding generation
        - Document-level context preservation
        - Batch indexing for performance optimization
        - Index update and deletion operations
        - Index optimization and statistics tracking
        - Health monitoring for indexer status

    See Also:
        - ProtocolAdaptiveChunker: Intelligent content chunking
        - ProtocolDirectKnowledgePipeline: Knowledge pipeline integration
        - ProtocolAnalyticsProvider: Indexing metrics and analytics
    """

    async def index_document(
        self, input_document: "ProtocolInputDocument"
    ) -> "ProtocolMultiVectorDocument":
        """
        Index a single document with multi-vector passage embeddings.

        Args:
            input_document: Input document to process and index

        Returns:
            Multi-vector document with passage-level embeddings
        """
        ...

    async def index_documents(
        self,
        input_documents: list["ProtocolInputDocument"],
    ) -> list["ProtocolMultiVectorDocument"]:
        """
        Batch index multiple documents with multi-vector passage embeddings.

        Args:
            input_documents: List of input documents to process and index

        Returns:
            List of multi-vector documents with passage-level embeddings
        """
        ...

    async def update_document_index(
        self, document_id: str, input_document: "ProtocolInputDocument"
    ) -> "ProtocolMultiVectorDocument":
        """
        Update an existing document's multi-vector index.

        Args:
            document_id: Existing document ID to update
            input_document: Updated document content

        Returns:
            Updated multi-vector document
        """
        ...

    async def delete_document_index(self, document_id: str) -> bool:
        """
        Delete a document's multi-vector index.
            ...
        Args:
            document_id: Document ID to delete

        Returns:
            True if deletion successful, False otherwise
        """
        ...

    async def optimize_index(self) -> "JsonType":
        """
        Optimize the multi-vector index for better performance.

        Returns:
            Dictionary with optimization statistics
        """
        ...

    async def get_index_statistics(self) -> "JsonType":
        """
        Get statistics about the multi-vector index.

        Returns:
            Dictionary with index statistics and metrics
        """
        ...

    async def health_check(self) -> "JsonType":
        """
        Perform health check for the indexer.

        Returns:
            Dictionary with health status information
        """
        ...
