"""
File handling protocol types for ONEX SPI interfaces.

Domain: File processing and writing protocols
"""

from pathlib import Path
from typing import Dict, Literal, Protocol, Union
from uuid import UUID

# File operation types
FileOperation = Literal["read", "write", "append", "delete", "move", "copy"]
FileStatus = Literal["exists", "missing", "locked", "corrupted", "accessible"]
ProcessingStatus = Literal["pending", "processing", "completed", "failed", "skipped"]

# File content types - more specific than Any
FileContent = Union[str, bytes]
FileMetadata = Union[str, int, float, bool]


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
    output_data: Dict[str, FileMetadata]


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
