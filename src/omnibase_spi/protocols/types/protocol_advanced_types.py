"""
Advanced processing types for ONEX SPI.

This module provides protocol interfaces for advanced processing operations
including output formatting, vector indexing, fixture loading, enum generation,
and knowledge pipeline operations.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import ContextValue

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


@runtime_checkable
class ProtocolAgentAction(Protocol):
    """Protocol for agent action definitions."""

    @property
    def action_id(self) -> str:
        """Action identifier."""
        ...

    @property
    def action_type(self) -> str:
        """Type of action."""
        ...

    @property
    def parameters(self) -> dict[str, ContextValue]:
        """Action parameters."""
        ...

    @property
    def timeout_ms(self) -> int:
        """Timeout in milliseconds."""
        ...

    @property
    def retry_count(self) -> int:
        """Retry count."""
        ...

    @property
    def required_capabilities(self) -> list[str]:
        """Required capabilities."""
        ...


@runtime_checkable
class ProtocolAIExecutionMetrics(Protocol):
    """Protocol for AI execution metrics."""

    @property
    def execution_id(self) -> UUID:
        """Execution identifier."""
        ...

    @property
    def model_name(self) -> str:
        """Model used."""
        ...

    async def input_tokens(self) -> int:
        """Input token count."""
        ...

    async def output_tokens(self) -> int:
        """Output token count."""
        ...

    @property
    def execution_time_ms(self) -> int:
        """Execution time."""
        ...

    @property
    def cost_estimate_usd(self) -> float:
        """Cost estimate in USD."""
        ...

    @property
    def success(self) -> bool:
        """Execution success status."""
        ...


@runtime_checkable
class ProtocolAgentDebugIntelligence(Protocol):
    """Protocol for agent debug intelligence."""

    @property
    def session_id(self) -> UUID:
        """Session identifier."""
        ...

    @property
    def agent_name(self) -> str:
        """Agent name."""
        ...

    @property
    def debug_data(self) -> dict[str, ContextValue]:
        """Debug data."""
        ...

    @property
    def performance_metrics(self) -> "ProtocolAIExecutionMetrics":
        """Performance metrics."""
        ...

    @property
    def error_logs(self) -> list[str]:
        """Error logs if any."""
        ...

    @property
    def suggestions(self) -> list[str]:
        """Debug suggestions."""
        ...


@runtime_checkable
class ProtocolPRTicket(Protocol):
    """Protocol for PR tickets."""

    @property
    def ticket_id(self) -> str:
        """Ticket identifier."""
        ...

    @property
    def title(self) -> str:
        """Ticket title."""
        ...

    @property
    def description(self) -> str:
        """Ticket description."""
        ...

    @property
    def priority(self) -> str:
        """Priority level."""
        ...

    @property
    def status(self) -> str:
        """Current status."""
        ...

    @property
    def assignee(self) -> str:
        """Assigned person."""
        ...


@runtime_checkable
class ProtocolVelocityLog(Protocol):
    """Protocol for velocity logs."""

    @property
    def log_id(self) -> UUID:
        """Log identifier."""
        ...

    @property
    def timestamp(self) -> str:
        """Log timestamp."""
        ...

    @property
    def metric_name(self) -> str:
        """Metric name."""
        ...

    @property
    def value(self) -> float:
        """Metric value."""
        ...

    @property
    def unit(self) -> str:
        """Metric unit."""
        ...

    @property
    def tags(self) -> list[str]:
        """Metric tags."""
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
class ProtocolIntelligenceResult(Protocol):
    """Protocol for intelligence analysis results."""

    @property
    def analysis_id(self) -> UUID:
        """Analysis identifier."""
        ...

    @property
    def confidence_score(self) -> float:
        """Confidence score."""
        ...

    @property
    def entities(self) -> list[dict[str, ContextValue]]:
        """Extracted entities."""
        ...

    @property
    def sentiment_score(self) -> float | None:
        """Sentiment analysis if available."""
        ...

    @property
    def language_detected(self) -> str | None:
        """Detected language."""
        ...

    @property
    def processing_metadata(self) -> dict[str, ContextValue]:
        """Processing metadata."""
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
LiteralActionType = str  # Would be a Literal in full implementation
