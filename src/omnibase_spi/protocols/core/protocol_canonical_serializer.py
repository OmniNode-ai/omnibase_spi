"""
Protocol for canonical serialization and normalization.

Provides a clean interface for canonical serialization operations without exposing
implementation-specific details. This protocol enables testing and cross-component
serialization while maintaining proper architectural boundaries.
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue

if TYPE_CHECKING:
    pass


@runtime_checkable
class ProtocolCanonicalSerializer(Protocol):
    """
    Protocol for canonical serialization and normalization of metadata blocks.
    Enforces protocol-compliant, deterministic serialization for stamping, hashing, and idempotency.
    All field references must use canonical field names, not string literals.
    Implementations may support YAML, JSON, or other formats.

    NOTE: This protocol uses TYPE_CHECKING and forward references to avoid circular imports
    while maintaining strong typing. This is the canonical pattern for all ONEX protocol interfaces.
    """

    def canonicalize_metadata_block(self, metadata_block: dict[str, Any]) -> str:
        """
        Canonicalize a metadata block for deterministic serialization and hash computation.
        - Accepts a dict[str, Any] or metadata block instance.
        - Replaces volatile fields (e.g., hash, last_modified_at) with a protocol placeholder.
        - Returns the canonical serialized string.
        """
        ...

    def normalize_body(self, body: str) -> str:
        """
        Canonical normalization for file body content.
        - Strips trailing spaces
        - Normalizes all line endings to '\n'
        - Ensures exactly one newline at EOF
        - Asserts only '\n' line endings are present
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
        """
        Canonicalize the full content (block + body) for hash computation.
        - Returns the canonical string to be hashed.
        """
        ...
