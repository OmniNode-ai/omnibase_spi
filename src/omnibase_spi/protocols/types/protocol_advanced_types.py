"""
Advanced processing types for ONEX SPI.

This module provides protocol interfaces for advanced processing operations
including output formatting, vector indexing, fixture loading, document handling,
and adaptive chunking operations.

Agent and AI-related types have been moved to protocol_agent_ai_types.py.
"""

from typing import Protocol, runtime_checkable
from uuid import UUID

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
from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolOutputFormat(Protocol):
    """
    Protocol for output format specifications.

    Defines the structure for describing output formats including file
    extensions, MIME types, and metadata support. Used for format
    negotiation and output serialization across ONEX systems.

    Attributes:
        format_name: Human-readable format name (e.g., "JSON", "Markdown").
        file_extension: Standard file extension (e.g., ".json", ".md").
        content_type: MIME content type (e.g., "application/json").
        supports_metadata: Whether format can embed metadata.

    Example:
        ```python
        class JsonFormat:
            '''JSON output format specification.'''

            @property
            def format_name(self) -> str:
                return "JSON"

            @property
            def file_extension(self) -> str:
                return ".json"

            @property
            def content_type(self) -> str:
                return "application/json"

            @property
            def supports_metadata(self) -> bool:
                return True  # Can embed metadata as fields

        fmt = JsonFormat()
        assert isinstance(fmt, ProtocolOutputFormat)
        ```
    """

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
    """
    Protocol for output data structures.

    Encapsulates generated output content with metadata, format information,
    and tracing data. Used for returning processed results from nodes and
    tools with full provenance tracking.

    Attributes:
        content: The main output content as a string.
        metadata: Key-value pairs describing the output.
        format_type: Specification of the output format.
        timestamp: ISO timestamp of when output was generated.
        correlation_id: UUID for request correlation and tracing.

    Example:
        ```python
        class ReportOutput:
            '''Generated report output.'''

            @property
            def content(self) -> str:
                return "# Monthly Report\\n\\nSummary of activities..."

            @property
            def metadata(self) -> dict:
                return {"title": "Monthly Report", "pages": 5}

            @property
            def format_type(self) -> ProtocolOutputFormat:
                return MarkdownFormat()

            @property
            def timestamp(self) -> str:
                return "2024-01-15T10:30:00Z"

            @property
            def correlation_id(self) -> UUID:
                return UUID("550e8400-e29b-41d4-a716-446655440000")

        output = ReportOutput()
        assert isinstance(output, ProtocolOutputData)
        ```
    """

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
    """
    Protocol for multi-vector document representation.

    Represents a document with multiple vector embeddings for different
    aspects or models. Used in RAG systems and semantic search where
    documents may have embeddings for content, title, summary, etc.

    Attributes:
        document_id: Unique identifier for the document.
        content_vectors: Map of embedding type to vector (e.g., "title": [...]).
        metadata: Document metadata and properties.
        chunk_info: Information about how document was chunked.
        embedding_models: List of models used to generate embeddings.

    Example:
        ```python
        class IndexedDocument:
            '''Document with multiple semantic embeddings.'''

            @property
            def document_id(self) -> UUID:
                return UUID("550e8400-e29b-41d4-a716-446655440000")

            @property
            def content_vectors(self) -> dict[str, list[float]]:
                return {
                    "title": [0.1, 0.2, 0.3, ...],  # 384-dim
                    "content": [0.4, 0.5, 0.6, ...],  # 768-dim
                    "summary": [0.7, 0.8, 0.9, ...]  # 384-dim
                }

            @property
            def metadata(self) -> dict:
                return {"source": "knowledge_base", "author": "Alice"}

            @property
            def chunk_info(self) -> dict:
                return {"chunk_size": 512, "overlap": 50}

            @property
            def embedding_models(self) -> list[str]:
                return ["sentence-transformers/all-MiniLM-L6-v2"]

        doc = IndexedDocument()
        assert isinstance(doc, ProtocolMultiVectorDocument)
        ```
    """

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
    """
    Protocol for input document processing.

    Represents a document to be processed including its content, type,
    source location, and metadata. Used as input to document processing
    pipelines, indexing systems, and transformation nodes.

    Attributes:
        document_id: Unique identifier for tracking the document.
        content: The raw document content.
        content_type: MIME type of the content (e.g., "text/plain").
        metadata: Additional document properties and context.
        source_uri: Original location or source of the document.

    Example:
        ```python
        class PdfDocument:
            '''PDF document for processing.'''

            @property
            def document_id(self) -> UUID:
                return UUID("550e8400-e29b-41d4-a716-446655440000")

            @property
            def content(self) -> str:
                return "Extracted text from the PDF..."

            @property
            def content_type(self) -> str:
                return "application/pdf"

            @property
            def metadata(self) -> dict:
                return {"title": "Report", "pages": 10, "author": "Bob"}

            @property
            def source_uri(self) -> str:
                return "s3://bucket/documents/report.pdf"

        doc = PdfDocument()
        assert isinstance(doc, ProtocolInputDocument)
        ```
    """

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
    """
    Protocol for test fixture data.

    Defines test fixtures with setup/teardown lifecycle, dependencies,
    and data payloads. Used in testing frameworks for consistent test
    environment preparation and cleanup.

    Attributes:
        fixture_id: Unique identifier for the fixture.
        fixture_type: Category of fixture (e.g., "database", "mock", "file").
        data: The actual fixture data payload.
        dependencies: Other fixtures this fixture depends on.
        setup_actions: Actions to perform during setup.
        teardown_actions: Actions to perform during cleanup.

    Example:
        ```python
        class DatabaseFixture:
            '''Test database fixture with sample data.'''

            @property
            def fixture_id(self) -> str:
                return "test_db_users"

            @property
            def fixture_type(self) -> str:
                return "database"

            @property
            def data(self) -> dict:
                return {
                    "users": [
                        {"id": 1, "name": "Alice"},
                        {"id": 2, "name": "Bob"}
                    ]
                }

            @property
            def dependencies(self) -> list[str]:
                return ["test_db_schema"]

            @property
            def setup_actions(self) -> list[str]:
                return ["truncate_table", "insert_data"]

            @property
            def teardown_actions(self) -> list[str]:
                return ["truncate_table"]

        fixture = DatabaseFixture()
        assert isinstance(fixture, ProtocolFixtureData)
        ```
    """

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
    """
    Protocol for schema definitions.

    Defines data schemas with field definitions, validation rules, and
    relationships. Used for data modeling, validation, and documentation
    generation across ONEX systems.

    Attributes:
        schema_name: Unique name for the schema.
        schema_version: Version string for the schema definition.
        fields: Map of field names to their type definitions.
        validation_rules: List of validation constraints.
        relationships: Foreign key and relationship definitions.

    Example:
        ```python
        class UserSchema:
            '''Schema definition for User data model.'''

            @property
            def schema_name(self) -> str:
                return "User"

            @property
            def schema_version(self) -> str:
                return "1.0.0"

            @property
            def fields(self) -> dict:
                return {
                    "id": {"type": "uuid", "primary_key": True},
                    "name": {"type": "string", "max_length": 100},
                    "email": {"type": "string", "format": "email"}
                }

            @property
            def validation_rules(self) -> list:
                return [
                    {"field": "email", "rule": "unique"},
                    {"field": "name", "rule": "required"}
                ]

            @property
            def relationships(self) -> dict:
                return {"orders": {"type": "one_to_many", "target": "Order"}}

        schema = UserSchema()
        assert isinstance(schema, ProtocolSchemaDefinition)
        ```
    """

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
    """
    Protocol for contract documents.

    Represents a contractual agreement between parties with terms,
    effective dates, and expiration information. Used for SLA definitions,
    service agreements, and inter-service contracts in ONEX.

    Attributes:
        contract_id: Unique identifier for the contract.
        contract_type: Category of contract (e.g., "SLA", "API", "service").
        parties: List of parties involved in the contract.
        terms: Dictionary of contract terms and conditions.
        effective_date: ISO date when contract becomes active.
        expiration_date: ISO date when contract expires (if applicable).

    Example:
        ```python
        class ServiceContract:
            '''SLA contract for compute service.'''

            @property
            def contract_id(self) -> UUID:
                return UUID("550e8400-e29b-41d4-a716-446655440000")

            @property
            def contract_type(self) -> str:
                return "SLA"

            @property
            def parties(self) -> list[str]:
                return ["compute-service", "orchestrator"]

            @property
            def terms(self) -> dict:
                return {
                    "uptime_sla": "99.9%",
                    "max_latency_ms": 100,
                    "rate_limit": 1000
                }

            @property
            def effective_date(self) -> str:
                return "2024-01-01"

            @property
            def expiration_date(self) -> str | None:
                return "2024-12-31"

        contract = ServiceContract()
        assert isinstance(contract, ProtocolContractDocument)
        ```
    """

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
    """
    Protocol for indexing configuration.

    Defines parameters for document chunking and indexing operations
    including chunk sizes, overlap settings, and preprocessing options.
    Used for configuring RAG pipelines and vector indexing systems.

    Attributes:
        chunk_size: Target size for each chunk in tokens/characters.
        chunk_overlap: Number of tokens/characters to overlap between chunks.
        strategy: Chunking strategy (e.g., "fixed", "sentence", "semantic").
        metadata_extraction: Whether to extract metadata from documents.
        preprocessing_options: Additional preprocessing configuration.

    Example:
        ```python
        class SemanticChunkingConfig:
            '''Configuration for semantic document chunking.'''

            @property
            def chunk_size(self) -> int:
                return 512

            @property
            def chunk_overlap(self) -> int:
                return 50

            @property
            def strategy(self) -> str:
                return "semantic"

            @property
            def metadata_extraction(self) -> bool:
                return True

            @property
            def preprocessing_options(self) -> dict:
                return {
                    "remove_headers": True,
                    "normalize_whitespace": True,
                    "extract_titles": True
                }

        config = SemanticChunkingConfig()
        assert isinstance(config, ProtocolIndexingConfiguration)
        ```
    """

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
    """
    Protocol for adaptive chunk results.

    Represents a single chunk from an adaptive chunking operation with
    position information, content, and optional embedding vectors. Used
    in document processing pipelines for semantic search and retrieval.

    Attributes:
        chunk_id: Unique identifier for this chunk.
        content: The text content of the chunk.
        start_position: Start character position in the original document.
        end_position: End character position in the original document.
        metadata: Additional chunk metadata (e.g., headings, section).
        embedding_vector: Pre-computed embedding vector if available.

    Example:
        ```python
        class DocumentChunk:
            '''A chunk from semantic document processing.'''

            @property
            def chunk_id(self) -> UUID:
                return UUID("550e8400-e29b-41d4-a716-446655440000")

            @property
            def content(self) -> str:
                return "This section discusses the core architecture..."

            @property
            def start_position(self) -> int:
                return 1024

            @property
            def end_position(self) -> int:
                return 1536

            @property
            def metadata(self) -> dict:
                return {"section": "Architecture", "heading_level": 2}

            @property
            def embedding_vector(self) -> list[float] | None:
                return [0.1, 0.2, 0.3, ...]  # 384-dimensional vector

        chunk = DocumentChunk()
        assert isinstance(chunk, ProtocolAdaptiveChunk)
        ```
    """

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
    """
    Protocol for chunking quality metrics.

    Provides quality assessment metrics for document chunking operations
    including coherence, semantic density, and coverage scores. Used for
    evaluating and optimizing chunking strategies.

    Attributes:
        total_chunks: Total number of chunks produced.
        average_chunk_size: Mean size of chunks in tokens/characters.
        quality_score: Overall quality score (0.0 to 1.0).
        coherence_score: Measure of semantic coherence within chunks.
        semantic_density: Information density per chunk.
        metadata_coverage: Percentage of chunks with extracted metadata.

    Example:
        ```python
        class ChunkingMetrics:
            '''Quality metrics for a chunking operation.'''

            @property
            def total_chunks(self) -> int:
                return 45

            @property
            def average_chunk_size(self) -> float:
                return 487.5

            @property
            def quality_score(self) -> float:
                return 0.92

            @property
            def coherence_score(self) -> float:
                return 0.88

            @property
            def semantic_density(self) -> float:
                return 0.75

            @property
            def metadata_coverage(self) -> float:
                return 0.95  # 95% of chunks have metadata

        metrics = ChunkingMetrics()
        assert isinstance(metrics, ProtocolChunkingQualityMetrics)
        if metrics.quality_score < 0.8:
            print("Consider adjusting chunking parameters")
        ```
    """

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

__all__ = [
    # Re-exported from protocol_agent_ai_types
    "LiteralActionType",
    "LiteralContractType",
    "LiteralDocumentType",
    "LiteralFixtureType",
    # Type aliases
    "LiteralOutputFormat",
    "ProtocolAIExecutionMetrics",
    "ProtocolAdaptiveChunk",
    "ProtocolAgentAction",
    "ProtocolAgentDebugIntelligence",
    "ProtocolChunkingQualityMetrics",
    "ProtocolContractDocument",
    "ProtocolFixtureData",
    "ProtocolIndexingConfiguration",
    "ProtocolInputDocument",
    "ProtocolIntelligenceResult",
    "ProtocolMultiVectorDocument",
    "ProtocolOutputData",
    # Protocols defined in this module
    "ProtocolOutputFormat",
    "ProtocolPRTicket",
    "ProtocolSchemaDefinition",
    "ProtocolVelocityLog",
]
