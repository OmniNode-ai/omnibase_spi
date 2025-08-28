"""
File handling protocol types for ONEX SPI interfaces.

Domain: File processing and writing protocols
"""

from pathlib import Path
from typing import Dict, List, Literal, Optional, Protocol, Union
from uuid import UUID

# File operation types
FileOperation = Literal["read", "write", "append", "delete", "move", "copy"]
FileStatus = Literal["exists", "missing", "locked", "corrupted", "accessible"]
ProcessingStatus = Literal["pending", "processing", "completed", "failed", "skipped"]

# File content types - more specific than Any
FileContent = Union[str, bytes]


# File metadata protocol for type safety
class ProtocolFileMetadata(Protocol):
    """Protocol for file metadata with type-safe access."""

    def get_size(self) -> int:
        ...

    def get_mime_type(self) -> str:
        ...

    def get_encoding(self) -> Optional[str]:
        ...

    def get_created_at(self) -> float:
        ...

    def get_modified_at(self) -> float:
        ...


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
    """Protocol for handler matching results."""

    handler_id: UUID
    handler_name: str
    match_confidence: float
    can_handle: bool
    required_capabilities: list[str]


# Protocol types for file type handlers
class ProtocolCanHandleResult(Protocol):
    """Protocol for can handle determination results."""

    can_handle: bool
    confidence: float
    reason: str
    file_metadata: ProtocolFileMetadata


class ProtocolHandlerMetadata(Protocol):
    """Protocol for handler metadata."""

    name: str
    version: str
    author: str
    description: str
    supported_extensions: List[str]
    supported_filenames: List[str]
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
    version: str
    file_metadata: ProtocolFileMetadata


# Result data protocol for type safety
class ProtocolResultData(Protocol):
    """Protocol for operation result data."""

    def get_output_path(self) -> Optional[Path]:
        ...

    def get_processed_files(self) -> List[Path]:
        ...

    def get_metrics(self) -> Dict[str, float]:
        ...

    def get_warnings(self) -> List[str]:
        ...


class ProtocolOnexResult(Protocol):
    """Protocol for ONEX operation results."""

    success: bool
    message: str
    result_data: Optional[ProtocolResultData]
    error_code: Optional[str]
    timestamp: float
