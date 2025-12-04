"""
File result and handler protocol types for ONEX SPI interfaces.

Domain: File processing results, handler metadata, and operation results
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ProtocolDateTime,
        ProtocolSemVer,
    )

from omnibase_spi.protocols.types.protocol_core_types import LiteralBaseStatus
from omnibase_spi.protocols.types.protocol_file_handling_types import (
    LiteralFileOperation,
    ProtocolFileMetadata,
)

ProcessingStatus = LiteralBaseStatus


@runtime_checkable
class ProtocolProcessingResult(Protocol):
    """Protocol for file processing results."""

    file_path: str
    operation: LiteralFileOperation
    status: ProcessingStatus
    processing_time: float
    error_message: str | None
    file_metadata: ProtocolFileMetadata


@runtime_checkable
class ProtocolFileTypeResult(Protocol):
    """Protocol for file type detection results."""

    file_path: str
    detected_type: str
    confidence: float
    mime_type: str
    is_supported: bool
    error_message: str | None


@runtime_checkable
class ProtocolHandlerMatch(Protocol):
    """Protocol for node matching results."""

    node_id: UUID
    node_name: str
    match_confidence: float
    can_handle: bool
    required_capabilities: list[str]


@runtime_checkable
class ProtocolCanHandleResult(Protocol):
    """Protocol for can handle determination results."""

    can_handle: bool
    confidence: float
    reason: str
    file_metadata: ProtocolFileMetadata


@runtime_checkable
class ProtocolHandlerMetadata(Protocol):
    """Protocol for node metadata."""

    name: str
    version: "ProtocolSemVer"
    author: str
    description: str
    supported_extensions: list[str]
    supported_filenames: list[str]
    priority: int
    requires_content_analysis: bool


@runtime_checkable
class ProtocolResultData(Protocol):
    """Protocol for operation result data - attribute-based for data compatibility."""

    output_path: str | None
    processed_files: list[str]
    metrics: dict[str, float]
    warnings: list[str]


@runtime_checkable
class ProtocolOnexResult(Protocol):
    """Protocol for ONEX operation results."""

    success: bool
    message: str
    result_data: ProtocolResultData | None
    error_code: str | None
    timestamp: "ProtocolDateTime"


@runtime_checkable
class ProtocolResultOperations(Protocol):
    """Protocol for result operations - method-based for services."""

    def format_result(self, result: "ProtocolOnexResult") -> str: ...

    async def merge_results(
        self, results: list["ProtocolOnexResult"]
    ) -> ProtocolOnexResult: ...

    async def validate_result(self, result: "ProtocolOnexResult") -> bool: ...
