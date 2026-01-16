"""Protocol for ONEX metadata stamping operations.

This module defines the interface for stamping files with ONEX metadata blocks,
including cryptographic hashes, version information, and lifecycle tracking.
"""

from __future__ import annotations

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
