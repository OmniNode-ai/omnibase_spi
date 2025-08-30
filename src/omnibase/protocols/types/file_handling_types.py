"""
File handling protocol types for ONEX SPI interfaces.

Domain: File processing and writing protocols
"""

from pathlib import Path
from typing import Literal, Optional, Protocol
from uuid import UUID

from omnibase.protocols.types.core_types import (
    BaseStatus,
    ProtocolDateTime,
    ProtocolSemVer,
)

# File operation types
FileOperation = Literal["read", "write", "append", "delete", "move", "copy"]
FileStatus = Literal["exists", "missing", "locked", "corrupted", "accessible"]
ProcessingStatus = BaseStatus

# File content types - more specific than Any
FileContent = str | bytes


# File metadata protocol for type safety
class ProtocolFileMetadata(Protocol):
    """Protocol for file metadata - attribute-based for data compatibility."""

    size: int
    mime_type: str
    encoding: Optional[str]
    created_at: float
    modified_at: float


# File information protocols
class ProtocolFileInfo(Protocol):
    """Protocol for file information objects."""

    file_path: Path
    file_size: int
    file_type: str
    mime_type: str
    last_modified: float
    status: FileStatus


class ProtocolFileContent(Protocol):
    """Protocol for file content objects."""

    file_path: Path
    content: FileContent
    encoding: str | None
    content_hash: str
    is_binary: bool


# File processing protocols
class ProtocolProcessingResult(Protocol):
    """Protocol for file processing results."""

    file_path: Path
    operation: FileOperation
    status: ProcessingStatus
    processing_time: float
    error_message: str | None
    file_metadata: ProtocolFileMetadata


class ProtocolFileFilter(Protocol):
    """Protocol for file filtering criteria."""

    include_extensions: list[str]
    exclude_extensions: list[str]
    min_size: int | None
    max_size: int | None
    modified_after: float | None
    modified_before: float | None


# File type detection protocols
class ProtocolFileTypeResult(Protocol):
    """Protocol for file type detection results."""

    file_path: Path
    detected_type: str
    confidence: float
    mime_type: str
    is_supported: bool
    error_message: str | None


class ProtocolHandlerMatch(Protocol):
    """Protocol for node matching results."""

    node_id: UUID
    node_name: str
    match_confidence: float
    can_handle: bool
    required_capabilities: list[str]


# Protocol types for file type nodes
class ProtocolCanHandleResult(Protocol):
    """Protocol for can handle determination results."""

    can_handle: bool
    confidence: float
    reason: str
    file_metadata: ProtocolFileMetadata


class ProtocolHandlerMetadata(Protocol):
    """Protocol for node metadata."""

    name: str
    version: ProtocolSemVer
    author: str
    description: str
    supported_extensions: list[str]
    supported_filenames: list[str]
    priority: int
    requires_content_analysis: bool


class ProtocolExtractedBlock(Protocol):
    """Protocol for extracted block data."""

    content: str
    file_metadata: ProtocolFileMetadata
    block_type: str
    start_line: Optional[int]
    end_line: Optional[int]
    path: Path


class ProtocolSerializedBlock(Protocol):
    """Protocol for serialized block data."""

    serialized_data: str
    format: str
    version: ProtocolSemVer
    file_metadata: ProtocolFileMetadata


# Result data protocol for type safety
class ProtocolResultData(Protocol):
    """Protocol for operation result data - attribute-based for data compatibility."""

    output_path: Optional[Path]
    processed_files: list[Path]
    metrics: dict[str, float]
    warnings: list[str]


class ProtocolOnexResult(Protocol):
    """Protocol for ONEX operation results."""

    success: bool
    message: str
    result_data: Optional[ProtocolResultData]
    error_code: Optional[str]
    timestamp: ProtocolDateTime


# Behavior protocols for operations (method-based)
class ProtocolFileMetadataOperations(Protocol):
    """Protocol for file metadata operations - method-based for services."""

    def validate_metadata(self, metadata: ProtocolFileMetadata) -> bool: ...

    def serialize_metadata(self, metadata: ProtocolFileMetadata) -> str: ...

    def compare_metadata(
        self, meta1: ProtocolFileMetadata, meta2: ProtocolFileMetadata
    ) -> bool: ...


class ProtocolResultOperations(Protocol):
    """Protocol for result operations - method-based for services."""

    def format_result(self, result: ProtocolOnexResult) -> str: ...

    def merge_results(
        self, results: list[ProtocolOnexResult]
    ) -> ProtocolOnexResult: ...

    def validate_result(self, result: ProtocolOnexResult) -> bool: ...
