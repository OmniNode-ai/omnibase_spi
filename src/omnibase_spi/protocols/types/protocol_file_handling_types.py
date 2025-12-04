"""
File handling protocol types for ONEX SPI interfaces.

Domain: File content, metadata, and block protocols

Note: Result and handler protocols have been moved to protocol_file_result_types.py
and are re-exported here for backward compatibility.
"""

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ProtocolSemVer,
    )

LiteralFileOperation = Literal["read", "write", "append", "delete", "move", "copy"]
LiteralFileStatus = Literal["exists", "missing", "locked", "corrupted", "accessible"]


@runtime_checkable
class ProtocolFileContent(Protocol):
    """Protocol for file content values supporting validation and serialization."""

    async def validate_for_file(self) -> bool: ...

    def serialize_for_file(self) -> dict[str, object]: ...


@runtime_checkable
class ProtocolStringFileContent(ProtocolFileContent, Protocol):
    """Protocol for string-based file content (text files)."""

    value: str


@runtime_checkable
class ProtocolBinaryFileContent(ProtocolFileContent, Protocol):
    """Protocol for binary file content (binary files)."""

    value: bytes


FileContent = ProtocolFileContent


@runtime_checkable
class ProtocolFileMetadata(Protocol):
    """Protocol for file metadata - attribute-based for data compatibility."""

    size: int
    mime_type: str
    encoding: str | None
    created_at: float
    modified_at: float


@runtime_checkable
class ProtocolFileInfo(Protocol):
    """Protocol for file information objects."""

    file_path: str
    file_size: int
    file_type: str
    mime_type: str
    last_modified: float
    status: LiteralFileStatus


@runtime_checkable
class ProtocolFileContentObject(Protocol):
    """Protocol for file content objects."""

    file_path: str
    content: FileContent
    encoding: str | None
    content_hash: str
    is_binary: bool


@runtime_checkable
class ProtocolFileFilter(Protocol):
    """Protocol for file filtering criteria."""

    include_extensions: list[str]
    exclude_extensions: list[str]
    min_size: int | None
    max_size: int | None
    modified_after: float | None
    modified_before: float | None


@runtime_checkable
class ProtocolExtractedBlock(Protocol):
    """Protocol for extracted block data."""

    content: str
    file_metadata: ProtocolFileMetadata
    block_type: str
    start_line: int | None
    end_line: int | None
    path: str


@runtime_checkable
class ProtocolSerializedBlock(Protocol):
    """Protocol for serialized block data."""

    serialized_data: str
    format: str
    version: "ProtocolSemVer"
    file_metadata: ProtocolFileMetadata


@runtime_checkable
class ProtocolFileMetadataOperations(Protocol):
    """Protocol for file metadata operations - method-based for services."""

    async def validate_metadata(self, metadata: "ProtocolFileMetadata") -> bool: ...

    async def serialize_metadata(self, metadata: "ProtocolFileMetadata") -> str: ...

    async def compare_metadata(
        self, meta1: "ProtocolFileMetadata", meta2: "ProtocolFileMetadata"
    ) -> bool: ...


# Re-export protocols from protocol_file_result_types for backward compatibility
from omnibase_spi.protocols.types.protocol_file_result_types import (  # noqa: E402
    ProcessingStatus,
    ProtocolCanHandleResult,
    ProtocolFileTypeResult,
    ProtocolHandlerMatch,
    ProtocolHandlerMetadata,
    ProtocolOnexResult,
    ProtocolProcessingResult,
    ProtocolResultData,
    ProtocolResultOperations,
)
