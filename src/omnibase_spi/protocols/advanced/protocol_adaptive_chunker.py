"""
Protocol interface for adaptive chunkers in ONEX.

Defines the contract for LangExtract-enhanced adaptive chunking tools.
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_advanced_types import (
        ProtocolAdaptiveChunk,
        ProtocolChunkingQualityMetrics,
        ProtocolIndexingConfiguration,
        ProtocolIntelligenceResult,
    )


@runtime_checkable
class ProtocolAdaptiveChunker(Protocol):
    """Protocol for adaptive chunking tools."""

    def chunk_content_adaptive(
        self,
        content: str,
        config: "ProtocolIndexingConfiguration",
        intelligence_result: "ProtocolIntelligenceResult" | None = None,
        entities: list[Any] | None = None,
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
