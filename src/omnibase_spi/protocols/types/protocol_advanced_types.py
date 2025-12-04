"""
Advanced processing types for ONEX SPI.

This module provides protocol interfaces for advanced processing operations
including output formatting, vector indexing, fixture loading, document handling,
and adaptive chunking operations.

Agent and AI-related types have been moved to protocol_agent_ai_types.py.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import ContextValue

# Re-export agent/AI types for backward compatibility
from omnibase_spi.protocols.types.protocol_agent_ai_types import (
    LiteralActionType,
    ProtocolAgentAction,
    ProtocolAgentDebugIntelligence,
    ProtocolAIExecutionMetrics,
    ProtocolIntelligenceResult,
    ProtocolPRTicket,
    ProtocolVelocityLog,
)

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import LiteralHealthStatus


@runtime_checkable
class ProtocolOutputFormat(Protocol):
    """Protocol for output format specifications."""

    @property
    def format_name(self) -> str:
        """Name of the output format."""
        ...

    @property
    def file_extension(self) -> str:
        """File extension for this format."""
        ...

    @property
    def content_type(self) -> str:
        """MIME content type."""
        ...

    @property
    def supports_metadata(self) -> bool:
        """Whether format supports metadata embedding."""
        ...


@runtime_checkable
class ProtocolOutputData(Protocol):
    """Protocol for output data structures."""

    @property
    def content(self) -> str:
        """Main content output."""
        ...

    @property
    def metadata(self) -> dict[str, ContextValue]:
        """Output metadata."""
        ...

    @property
    def format_type(self) -> "ProtocolOutputFormat":
        """Output format specification."""
        ...

    @property
    def timestamp(self) -> str:
        """Generation timestamp."""
        ...

    @property
    def correlation_id(self) -> UUID:
        """Correlation ID for tracking."""
        ...


@runtime_checkable
class ProtocolMultiVectorDocument(Protocol):
    """Protocol for multi-vector document representation."""

    @property
    def document_id(self) -> UUID:
        """Unique document identifier."""
        ...

    @property
    def content_vectors(self) -> dict[str, list[float]]:
        """Content vectors by embedding type."""
        ...

    @property
    def metadata(self) -> dict[str, ContextValue]:
        """Document metadata."""
        ...

    @property
    def chunk_info(self) -> dict[str, ContextValue]:
        """Chunking information."""
        ...

    @property
    def embedding_models(self) -> list[str]:
        """Models used for embedding."""
        ...


@runtime_checkable
class ProtocolInputDocument(Protocol):
    """Protocol for input document processing."""

    @property
    def document_id(self) -> UUID:
        """Document identifier."""
        ...

    @property
    def content(self) -> str:
        """Document content."""
        ...

    @property
    def content_type(self) -> str:
        """Content type (MIME)."""
        ...

    @property
    def metadata(self) -> dict[str, ContextValue]:
        """Document metadata."""
        ...

    @property
    def source_uri(self) -> str:
        """Source URI."""
        ...


@runtime_checkable
class ProtocolFixtureData(Protocol):
    """Protocol for test fixture data."""

    @property
    def fixture_id(self) -> str:
        """Fixture identifier."""
        ...

    @property
    def fixture_type(self) -> str:
        """Type of fixture."""
        ...

    @property
    def data(self) -> dict[str, ContextValue]:
        """Fixture data content."""
        ...

    @property
    def dependencies(self) -> list[str]:
        """Required dependencies."""
        ...

    @property
    def setup_actions(self) -> list[str]:
        """Setup actions required."""
        ...

    @property
    def teardown_actions(self) -> list[str]:
        """Teardown actions required."""
        ...


@runtime_checkable
class ProtocolSchemaDefinition(Protocol):
    """Protocol for schema definitions."""

    @property
    def schema_name(self) -> str:
        """Schema name."""
        ...

    @property
    def schema_version(self) -> str:
        """Schema version."""
        ...

    @property
    def fields(self) -> dict[str, ContextValue]:
        """Field definitions."""
        ...

    @property
    def validation_rules(self) -> list[dict[str, ContextValue]]:
        """Validation rules."""
        ...

    @property
    def relationships(self) -> dict[str, ContextValue]:
        """Relationship definitions."""
        ...


@runtime_checkable
class ProtocolContractDocument(Protocol):
    """Protocol for contract documents."""

    @property
    def contract_id(self) -> UUID:
        """Contract identifier."""
        ...

    @property
    def contract_type(self) -> str:
        """Type of contract."""
        ...

    @property
    def parties(self) -> list[str]:
        """Involved parties."""
        ...

    @property
    def terms(self) -> dict[str, ContextValue]:
        """Contract terms."""
        ...

    @property
    def effective_date(self) -> str:
        """Effective date."""
        ...

    @property
    def expiration_date(self) -> str | None:
        """Expiration date if any."""
        ...


# Additional protocols for adaptive chunking
@runtime_checkable
class ProtocolIndexingConfiguration(Protocol):
    """Protocol for indexing configuration."""

    @property
    def chunk_size(self) -> int:
        """Target chunk size."""
        ...

    @property
    def chunk_overlap(self) -> int:
        """Chunk overlap size."""
        ...

    @property
    def strategy(self) -> str:
        """Chunking strategy."""
        ...

    @property
    def metadata_extraction(self) -> bool:
        """Whether to extract metadata."""
        ...

    @property
    def preprocessing_options(self) -> dict[str, ContextValue]:
        """Preprocessing options."""
        ...


@runtime_checkable
class ProtocolAdaptiveChunk(Protocol):
    """Protocol for adaptive chunk results."""

    @property
    def chunk_id(self) -> UUID:
        """Chunk identifier."""
        ...

    @property
    def content(self) -> str:
        """Chunk content."""
        ...

    @property
    def start_position(self) -> int:
        """Start position in original."""
        ...

    @property
    def end_position(self) -> int:
        """End position in original."""
        ...

    @property
    def metadata(self) -> dict[str, ContextValue]:
        """Chunk metadata."""
        ...

    @property
    def embedding_vector(self) -> list[float] | None:
        """Embedding vector if available."""
        ...


@runtime_checkable
class ProtocolChunkingQualityMetrics(Protocol):
    """Protocol for chunking quality metrics."""

    @property
    def total_chunks(self) -> int:
        """Total number of chunks."""
        ...

    @property
    def average_chunk_size(self) -> float:
        """Average chunk size."""
        ...

    @property
    def quality_score(self) -> float:
        """Overall quality score."""
        ...

    @property
    def coherence_score(self) -> float:
        """Coherence score."""
        ...

    @property
    def semantic_density(self) -> float:
        """Semantic density score."""
        ...

    @property
    def metadata_coverage(self) -> float:
        """Metadata coverage score."""
        ...


# Type aliases for common literal types
LiteralOutputFormat = str  # Would be a Literal in full implementation
LiteralDocumentType = str  # Would be a Literal in full implementation
LiteralFixtureType = str  # Would be a Literal in full implementation
LiteralContractType = str  # Would be a Literal in full implementation
