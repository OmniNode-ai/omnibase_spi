from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types import ProtocolNodeMetadata


@runtime_checkable
class ProtocolCanonicalSerializer(Protocol):
    """
    Protocol for canonical serialization and normalization of metadata blocks.
    Enforces protocol-compliant, deterministic serialization for stamping, hashing, and idempotency.
    All field references must use canonical Enums (e.g., NodeMetadataField), not string literals.
    Implementations may support YAML, JSON, or other formats.

    NOTE: This protocol uses TYPE_CHECKING and forward references for data types to avoid circular imports
    while maintaining strong typing. This is the canonical pattern for all ONEX protocol interfaces.
    """

    def canonicalize_metadata_block(
        self, metadata_block: dict[str, object] | object
    ) -> str: ...

    def normalize_body(self, body: str) -> str: ...

    def canonicalize_for_hash(
        self,
        block: "ProtocolNodeMetadata",
        body: str,
        volatile_fields: tuple[str, ...],
        placeholder: str,
    ) -> str: ...
