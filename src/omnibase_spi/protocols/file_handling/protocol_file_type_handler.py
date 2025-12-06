from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ProtocolNodeMetadata,
        ProtocolSemVer,
    )
    from omnibase_spi.protocols.types.protocol_file_handling_types import (
        ProtocolCanHandleResult,
        ProtocolExtractedBlock,
        ProtocolOnexResult,
        ProtocolSerializedBlock,
    )


@runtime_checkable
class ProtocolStampOptions(Protocol):
    """
    Protocol for stamping operation options in ONEX ecosystem.

    Defines the contract for configuration options that control
    stamping operations across different file types and handlers.

    Key Features:
        - Force stamping override controls
        - Backup creation for safety
        - Dry-run mode for validation
        - Consistent option interface across handlers

    Usage Example:
        ```python
        options: ProtocolStampOptions = SomeStampOptions()

        # Configure stamping behavior
        if options.force:
            # Override existing stamps
            pass
        if options.backup:
            # Create backup before stamping
            pass
        if options.dry_run:
            # Validate without making changes
            pass
        ```
    """

    force: bool
    backup: bool
    dry_run: bool


@runtime_checkable
class ProtocolValidationOptions(Protocol):
    """
    Protocol for validation operation options in ONEX ecosystem.

    Defines the contract for configuration options that control
    validation operations across different file types and handlers.

    Key Features:
        - Strict validation mode controls
        - Verbose output and logging
        - Syntax checking options
        - Consistent validation interface

    Usage Example:
        ```python
        options: ProtocolValidationOptions = SomeValidationOptions()

        # Configure validation behavior
        if options.strict:
            # Enable strict validation rules
            pass
        if options.verbose:
            # Enable detailed logging and output
            pass
        if options.check_syntax:
            # Enable syntax checking
            pass
        ```
    """

    strict: bool
    verbose: bool
    check_syntax: bool


@runtime_checkable
class ProtocolFileProcessingTypeHandler(Protocol):
    """
    Protocol for file type nodes in the ONEX stamper engine.
    All methods and metadata must use canonical result models per typing_and_protocols rule.

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        # NodePythonFileProcessor would implement the protocol interface
        # All methods defined in the protocol contract

        # Usage in application
        node: "ProtocolFileProcessingTypeHandler" = NodePythonFileProcessor()

        # Check if node can process a file
        result = node.can_handle("example.py", "file_content")
        if result.can_handle:
            # Extract, stamp, and validate file
            block = node.extract_block("example.py", "file_content")
            # ... implementation handles file operations
        ```

    Node Implementation Patterns:
        - File type detection: Extension-based, content-based, and heuristic analysis
        - Metadata extraction: Language-specific parsing (AST, regex, etc.)
        - Stamping workflow: Extract → Serialize → Inject → Validate
        - Validation modes: Syntax checking, metadata compliance, strict requirements
        - Error handling: Graceful degradation with detailed error messages
    """

    async def metadata(self) -> ProtocolNodeMetadata: ...

    @property
    def node_name(self) -> str: ...

    @property
    def node_version(self) -> ProtocolSemVer: ...

    @property
    def node_author(self) -> str: ...

    @property
    def node_description(self) -> str: ...

    @property
    def supported_extensions(self) -> list[str]: ...

    @property
    def supported_filenames(self) -> list[str]: ...

    @property
    def node_priority(self) -> int: ...

    @property
    def requires_content_analysis(self) -> bool: ...

    async def can_handle(self, path: str, content: str) -> ProtocolCanHandleResult: ...

    async def extract_block(
        self, path: str, content: str
    ) -> ProtocolExtractedBlock: ...

    async def serialize_block(
        self, meta: ProtocolExtractedBlock
    ) -> ProtocolSerializedBlock: ...

    async def normalize_rest(self, rest: str) -> str: ...

    async def stamp(
        self, path: str, content: str, options: ProtocolStampOptions
    ) -> ProtocolOnexResult: ...

    async def pre_validate(
        self, path: str, content: str, options: ProtocolValidationOptions
    ) -> ProtocolOnexResult | None: ...

    async def post_validate(
        self, path: str, content: str, options: ProtocolValidationOptions
    ) -> ProtocolOnexResult | None: ...

    async def validate(
        self, path: str, content: str, options: ProtocolValidationOptions
    ) -> ProtocolOnexResult: ...
