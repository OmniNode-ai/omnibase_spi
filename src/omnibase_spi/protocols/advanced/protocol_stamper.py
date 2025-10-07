# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.153817'
# description: Stamped by ToolPython
# entrypoint: python://protocol_stamper
# hash: 03d05f8af913336b06a9f083bcd45d5dc63dbb479b534d62047908932cbbf0ab
# last_modified_at: '2025-05-29T14:14:00.352908+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_stamper.py
# namespace: python://omnibase.protocol.protocol_stamper
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 4b93002d-dee8-4272-a3b6-d17d4ce909d7
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Any, Literal, Protocol, runtime_checkable

from omnibase_spi.protocols.types import ProtocolOnexResult

# Protocol for template type enumeration
LiteralTemplateType = Literal["MINIMAL", "STANDARD", "FULL", "CUSTOM"]


@runtime_checkable
class ProtocolTemplateTypeEnum(Protocol):
    """
    Protocol for template type enumeration in metadata stamping.

    Defines template types (MINIMAL, STANDARD, FULL, CUSTOM) and their
    associated configurations for metadata generation.

    Attributes:
        value: Template type value (e.g., "MINIMAL", "STANDARD")
        name: Template type name
    """

    value: str
    name: str

    def __str__(self) -> str: ...

    async def get_template_config(self) -> dict[str, object]: ...


@runtime_checkable
class ProtocolStamper(Protocol):
    """
    Protocol for stamping ONEX node metadata with hashes, signatures, and trace data.

    Defines the contract for metadata stamping operations that enrich files with
    OmniNode metadata blocks, including cryptographic hashes, version information,
    authorship, and lifecycle tracking. Enables consistent metadata management
    across the ONEX ecosystem.

    Example:
        ```python
        from omnibase_spi.protocols.advanced import ProtocolStamper
        from omnibase_spi.protocols.types import ProtocolOnexResult

        async def stamp_node_file(
            stamper: ProtocolStamper,
            file_path: str
        ) -> ProtocolOnexResult:
            # Stamp file with default metadata
            result = await stamper.stamp(file_path)

            if result.success:
                print(f"Successfully stamped: {file_path}")
                print(f"Hash: {result.data.get('hash')}")
            else:
                print(f"Stamping failed: {result.message}")

            return result
        ```

    Key Features:
        - Cryptographic hash generation and verification
        - Metadata block injection and update
        - Version tracking and lifecycle management
        - Authorship and ownership attribution
        - Template-based metadata customization
        - File integrity validation

    See Also:
        - ProtocolStamperEngine: Directory-level stamping operations
        - ProtocolOutputFormatter: Output formatting for stamped files
        - ProtocolContractAnalyzer: Contract metadata extraction
    """

    async def stamp(self, path: str) -> ProtocolOnexResult:
        """Stamp an ONEX metadata file at the given path."""
        ...

    async def stamp_file(
        self, file_path: str, metadata_block: dict[str, Any]
    ) -> ProtocolOnexResult:
        """
        Stamp the file with a metadata block, replacing any existing block.

        Args:
            file_path: Path to file to stamp
            metadata_block: Metadata dictionary to inject

        Returns:
            ProtocolOnexResult describing the operation result
        """
        ...
