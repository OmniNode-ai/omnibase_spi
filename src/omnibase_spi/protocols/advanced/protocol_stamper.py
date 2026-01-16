"""Protocol for ONEX metadata stamping operations.

This module defines the interface for stamping files with ONEX metadata blocks,
including cryptographic hashes, version information, and lifecycle tracking.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    pass

from omnibase_spi.protocols.types import ProtocolResult

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

    def __str__(self) -> str:
        """Return string representation of the template type.

        Returns:
            The template type value as a string (e.g., "MINIMAL", "STANDARD").
        """
        ...

    async def get_template_config(self) -> dict[str, object]:
        """Retrieve the configuration for this template type.

        Returns:
            Dictionary containing template configuration options including
            fields to include, formatting options, and metadata schema.

        Raises:
            ValueError: If the template type is not recognized.
        """
        ...


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
        from omnibase_spi.protocols.types import ProtocolResult

        async def stamp_node_file(
            stamper: ProtocolStamper,
            file_path: str
        ) -> ProtocolResult:
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

    async def stamp(self, path: str) -> ProtocolResult:
        """Stamp an ONEX metadata file at the given path.

        Generates and injects ONEX metadata block into the specified file,
        including cryptographic hash, version information, and lifecycle data.

        Args:
            path: Absolute or relative path to the file to stamp.

        Returns:
            ProtocolResult with success status and stamped metadata details
            including the generated hash, timestamp, and version information.

        Raises:
            FileNotFoundError: If the specified path does not exist.
            PermissionError: If the file cannot be read or written.
            ValueError: If the file format is not supported for stamping.
        """
        ...

    async def stamp_file(
        self, file_path: str, metadata_block: dict[str, Any]
    ) -> ProtocolResult:
        """Stamp the file with a metadata block, replacing any existing block.

        Args:
            file_path: Path to the file to stamp.
            metadata_block: Metadata dictionary to inject into the file.

        Returns:
            ProtocolResult with success status and operation details
            including the injected metadata summary.

        Raises:
            FileNotFoundError: If the specified file path does not exist.
            PermissionError: If the file cannot be read or written.
            ValueError: If the file format is not supported for stamping
                or the metadata block is invalid.
        """
        ...
