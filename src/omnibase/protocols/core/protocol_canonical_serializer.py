# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.112424'
# description: Stamped by NodePython
# entrypoint: python://protocol_canonical_serializer
# hash: 708077b54c6495b16cebfc3a5236b6bb7b817f62d5d819f739a822b14d1db345
# last_modified_at: '2025-05-29T14:14:00.185820+00:00'
# lifecycle: active
# meta_type: node
# metadata_version: 0.1.0
# name: protocol_canonical_serializer.py
# namespace: python://omnibase.protocol.protocol_canonical_serializer
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 8bb7045d-81a5-4bd7-922b-9fc361f650bf
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Protocol, Tuple

from omnibase.protocols.types import ProtocolNodeMetadata


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
        self,
        block: ProtocolNodeMetadata,
        volatile_fields: Tuple[str, ...],
        placeholder: str,
    ) -> str:
        """
        Canonicalize a metadata block for deterministic serialization and hash computation.
        - Accepts a dict or data instance.
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
        block: ProtocolNodeMetadata,
        body: str,
        volatile_fields: Tuple[str, ...],
        placeholder: str,
    ) -> str:
        """
        Canonicalize the full content (block + body) for hash computation.
        - Returns the canonical string to be hashed.
        """
        ...
