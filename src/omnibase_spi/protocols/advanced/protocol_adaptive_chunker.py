"""
Protocol interface for adaptive chunkers in ONEX.

Defines the contract for LangExtract-enhanced adaptive chunking tools.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_advanced_types import (
        ProtocolAdaptiveChunk,
        ProtocolChunkingQualityMetrics,
        ProtocolIndexingConfiguration,
        ProtocolIntelligenceResult,
    )


@runtime_checkable
class ProtocolAdaptiveChunker(Protocol):
    """
    Protocol for adaptive content chunking with intelligence-driven optimization.

    Defines the contract for LangExtract-enhanced adaptive chunking tools that
    intelligently segment content based on semantic boundaries, entity recognition,
    and configurable chunking strategies. Enables optimal content segmentation for
    indexing, retrieval, and analysis workflows.

    Example:
        ```python
        from omnibase_spi.protocols.advanced import ProtocolAdaptiveChunker
        from omnibase_spi.protocols.types import ProtocolIndexingConfiguration

        async def chunk_document(
            chunker: ProtocolAdaptiveChunker,
            document: str,
            config: ProtocolIndexingConfiguration
        ) -> list["ProtocolAdaptiveChunk"]:
            # Perform adaptive chunking with default configuration
            chunks, metrics = chunker.chunk_content_adaptive(
                content=document,
                config=config
            )

            # Log quality metrics
            print(f"Generated {len(chunks)} chunks")
            print(f"Average chunk size: {metrics.avg_chunk_size}")
            print(f"Quality score: {metrics.quality_score}")

            return chunks
        ```

    Key Features:
        - Intelligence-driven chunking based on semantic boundaries
        - Entity-aware segmentation for improved context preservation
        - Quality metrics tracking for chunking optimization
        - Configurable chunking strategies and size targets
        - LangExtract integration for enhanced content understanding

    See Also:
        - ProtocolMultiVectorIndexer: Multi-vector indexing for chunked content
        - ProtocolDirectKnowledgePipeline: Knowledge pipeline integration
        - ProtocolIndexingConfiguration: Chunking configuration options
    """

    def chunk_content_adaptive(
        self,
        content: str,
        config: "ProtocolIndexingConfiguration",
        intelligence_result: "ProtocolIntelligenceResult | None" = None,
        entities: list[object] | None = None,
    ) -> tuple[list["ProtocolAdaptiveChunk"], "ProtocolChunkingQualityMetrics"]:
        """
        Perform LangExtract-enhanced adaptive chunking.

        Args:
            content: Text content to chunk
            config: Chunking configuration
            intelligence_result: LangExtract intelligence analysis
            entities: Extracted entities from content

        Returns:
            Tuple of (chunks, metrics)
        """
        ...
