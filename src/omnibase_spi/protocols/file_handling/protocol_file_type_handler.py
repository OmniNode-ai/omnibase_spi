# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.169382'
# description: Stamped by NodePython
# entrypoint: python://protocol_file_type_node
# hash: f865199088b42907bcfd03147a6071a4ec1c21659e83436e8b30537c67f30d6c
# last_modified_at: '2025-05-29T14:14:00.255085+00:00'
# lifecycle: active
# meta_type: node
# metadata_version: 0.1.0
# name: protocol_file_type_node.py
# namespace: python://omnibase_spi.protocol.protocol_file_type_node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 4e1063a3-c759-42a8-8a3f-2d05489e0ea4
# version: 1.0.0
# === /OmniNode:Metadata ===


from __future__ import annotations

from pathlib import Path
from typing import Optional, Protocol, runtime_checkable

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
    """Protocol for stamping operation options."""

    force: bool
    backup: bool
    dry_run: bool


@runtime_checkable
class ProtocolValidationOptions(Protocol):
    """Protocol for validation operation options."""

    strict: bool
    verbose: bool
    check_syntax: bool


class ProtocolFileTypeHandler(Protocol):
    """
    Protocol for file type nodes in the ONEX stamper engine.
    All methods and metadata must use canonical result models per typing_and_protocols rule.

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        class NodePythonFileProcessor:
            @property
            def metadata(self) -> ProtocolNodeMetadata:
                # Implementation would return configured metadata
                ...

            @property
            def node_name(self) -> str:
                # Implementation returns node identifier
                ...

            def can_handle(self, path: Path, content: str) -> ProtocolCanHandleResult:
                # Implementation determines if file can be processed
                ...

            def extract_block(self, path: Path, content: str) -> ProtocolExtractedBlock:
                # Implementation extracts structured block from file content
                ...

            def stamp(self, path: Path, content: str, options: ProtocolStampOptions) -> ProtocolOnexResult:
                # Implementation adds metadata stamp to file
                ...

            def validate(self, path: Path, content: str, options: ProtocolValidationOptions) -> ProtocolOnexResult:
                # Implementation validates file content and metadata
                ...

        # Usage in application
        node: ProtocolFileTypeHandler = NodePythonFileProcessor()

        # Check if node can process a file
        result = node.can_handle(Path("example.py"), "file_content")
        if result.can_handle:
            # Extract, stamp, and validate file
            block = node.extract_block(Path("example.py"), "file_content")
            # ... implementation handles file operations
        ```

    Node Implementation Patterns:
        - File type detection: Extension-based, content-based, and heuristic analysis
        - Metadata extraction: Language-specific parsing (AST, regex, etc.)
        - Stamping workflow: Extract → Serialize → Inject → Validate
        - Validation modes: Syntax checking, metadata compliance, strict requirements
        - Error handling: Graceful degradation with detailed error messages
    """

    @property
    def metadata(self) -> ProtocolNodeMetadata: ...

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

    def can_handle(self, path: Path, content: str) -> ProtocolCanHandleResult: ...

    def extract_block(self, path: Path, content: str) -> ProtocolExtractedBlock: ...

    def serialize_block(
        self, meta: ProtocolExtractedBlock
    ) -> ProtocolSerializedBlock: ...

    def normalize_rest(self, rest: str) -> str: ...

    def stamp(
        self, path: Path, content: str, options: ProtocolStampOptions
    ) -> ProtocolOnexResult: ...

    def pre_validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> Optional[ProtocolOnexResult]: ...

    def post_validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> Optional[ProtocolOnexResult]: ...

    def validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> ProtocolOnexResult: ...
