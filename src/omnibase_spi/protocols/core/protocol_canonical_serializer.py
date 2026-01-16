"""
Protocol for canonical serialization and normalization.

Provides a clean interface for canonical serialization operations without exposing
implementation-specific details. This protocol enables testing and cross-component
serialization while maintaining proper architectural boundaries.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue

if TYPE_CHECKING:
    from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolCanonicalSerializer(Protocol):
    """
    Protocol for deterministic canonical serialization and content normalization.

    Provides consistent, reproducible serialization for metadata blocks and content
    bodies, enabling deterministic hash computation, content stamping, and idempotency
    verification across all ONEX components. This protocol ensures that identical
    logical content always produces identical serialized output regardless of
    formatting variations.

    The canonical serializer is essential for:
    - Deterministic content hashing and integrity verification
    - Metadata block stamping for provenance tracking
    - Idempotency detection in distributed operations
    - Content normalization across different sources
    - Reproducible serialization for testing and validation

    Example:
        ```python
        serializer: "ProtocolCanonicalSerializer" = get_canonical_serializer()

        # Canonicalize metadata for hashing
        metadata = {
            "name": "workflow_processor",
            "version": "1.0.0",
            "hash": "abc123",  # Volatile field
            "last_modified_at": "2025-01-01T00:00:00Z"  # Volatile field
        }
        canonical_metadata = serializer.canonicalize_metadata_block(metadata)
        # Volatile fields replaced with placeholders for deterministic hashing

        # Normalize body content
        body_content = "line1\\r\\nline2  \\nline3"
        normalized_body = serializer.normalize_body(body_content)
        # Returns: "line1\\nline2\\nline3\\n" (normalized line endings, trimmed spaces)

        # Full canonicalization for hash computation
        canonical_content = serializer.canonicalize_for_hash(
            block=metadata,
            body=body_content,
            volatile_fields=("hash", "last_modified_at"),
            placeholder="<REDACTED>"
        )
        # Produces deterministic output for hashing
        content_hash = hashlib.sha256(canonical_content.encode()).hexdigest()
        ```

    Key Features:
        - Deterministic serialization output for identical logical content
        - Volatile field replacement with configurable placeholders
        - Line ending normalization (CRLF -> LF)
        - Trailing whitespace removal
        - EOF newline enforcement
        - Support for multiple serialization formats (YAML, JSON)
        - Reproducible hash computation foundation

    Normalization Rules:
        - All line endings normalized to LF (\\n)
        - Trailing spaces removed from each line
        - Exactly one newline at end of file
        - Consistent field ordering in metadata blocks
        - Volatile fields replaced with placeholders

    Volatile Fields:
        Fields that change frequently and should be excluded from hashing:
        - hash: The computed hash value itself
        - last_modified_at: Timestamps that change on each update
        - updated_at, modified_at: Similar timestamp fields
        - etag: HTTP entity tag values

    See Also:
        - ProtocolLogger: Structured logging with canonical formats
        - ProtocolPerformanceMetrics: Metric serialization patterns
        - ProtocolObservability: Observability data normalization

    NOTE: This protocol uses TYPE_CHECKING and forward references to avoid circular
    imports while maintaining strong typing. This is the canonical pattern for all
    ONEX protocol interfaces.
    """

    def canonicalize_metadata_block(self, metadata_block: "JsonType") -> str:
        """Canonicalize a metadata block for deterministic serialization and hash computation.

        Accepts a JsonType or metadata block instance and replaces volatile fields
        (e.g., hash, last_modified_at) with a protocol placeholder.

        Args:
            metadata_block: The metadata block to canonicalize, as a JSON-compatible dict.

        Returns:
            The canonical serialized string representation.

        Raises:
            SPIError: When the metadata block cannot be serialized due to
                invalid structure or unsupported content types.
        """
        ...

    def normalize_body(self, body: str) -> str:
        """Canonical normalization for file body content.

        Performs the following normalizations:
        - Strips trailing spaces from each line
        - Normalizes all line endings to LF ('\\n')
        - Ensures exactly one newline at EOF
        - Validates only LF line endings are present

        Args:
            body: The raw body content string to normalize.

        Returns:
            The normalized body content with consistent line endings.

        Raises:
            SPIError: When the body content cannot be normalized due to
                encoding issues or invalid content.
        """
        ...

    def canonicalize_for_hash(
        self,
        block: dict[str, "ContextValue"],
        body: str,
        volatile_fields: tuple[str, ...] = (
            "hash",
            "last_modified_at",
        ),
        placeholder: str | None = None,
        **kwargs: "ContextValue",
    ) -> str:
        """Canonicalize the full content (block + body) for hash computation.

        Combines the metadata block and body content into a single canonical
        string suitable for deterministic hash computation.

        Args:
            block: The metadata block dictionary to canonicalize.
            body: The body content string to normalize and include.
            volatile_fields: Tuple of field names to replace with placeholders.
            placeholder: Custom placeholder string for volatile fields.
            **kwargs: Additional context values to include in canonicalization.

        Returns:
            The canonical string to be hashed.

        Raises:
            SPIError: When canonicalization fails due to invalid block structure,
                body content issues, or incompatible context values.
        """
        ...
