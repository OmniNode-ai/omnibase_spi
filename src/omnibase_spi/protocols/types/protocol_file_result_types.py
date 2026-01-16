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
    """
    Protocol for file processing operation results.

    Captures the complete outcome of a file processing operation including
    status, timing metrics, error information, and associated metadata.
    Used throughout ONEX for tracking file operation outcomes.

    Attributes:
        file_path: Path to the processed file.
        operation: Type of operation performed (read, write, etc.).
        status: Processing status (success, pending, failed, etc.).
        processing_time: Duration of processing in seconds.
        error_message: Error details if operation failed, None otherwise.
        file_metadata: Metadata of the processed file.

    Example:
        ```python
        class WriteResult:
            file_path: str = "/data/output.json"
            operation: LiteralFileOperation = "write"
            status: ProcessingStatus = "success"
            processing_time: float = 0.125
            error_message: str | None = None
            file_metadata: ProtocolFileMetadata = metadata_impl

        result = WriteResult()
        assert isinstance(result, ProtocolProcessingResult)
        ```
    """

    file_path: str
    operation: LiteralFileOperation
    status: ProcessingStatus
    processing_time: float
    error_message: str | None
    file_metadata: ProtocolFileMetadata


@runtime_checkable
class ProtocolFileTypeResult(Protocol):
    """
    Protocol for file type detection and analysis results.

    Contains the outcome of file type detection operations, including
    confidence scoring and support status. Used for routing files to
    appropriate handlers and validating file compatibility.

    Attributes:
        file_path: Path to the analyzed file.
        detected_type: Detected file type classification.
        confidence: Detection confidence score (0.0 to 1.0).
        mime_type: Detected MIME type string.
        is_supported: Whether the file type is supported for processing.
        error_message: Error details if detection failed, None otherwise.

    Example:
        ```python
        class JsonTypeResult:
            file_path: str = "/data/config.json"
            detected_type: str = "json"
            confidence: float = 0.98
            mime_type: str = "application/json"
            is_supported: bool = True
            error_message: str | None = None

        result = JsonTypeResult()
        assert isinstance(result, ProtocolFileTypeResult)
        ```
    """

    file_path: str
    detected_type: str
    confidence: float
    mime_type: str
    is_supported: bool
    error_message: str | None


@runtime_checkable
class ProtocolHandlerMatch(Protocol):
    """
    Protocol for node/handler matching results in file processing.

    Represents the outcome of matching a file to an appropriate handler
    node, including confidence scoring and capability requirements.
    Used for handler selection and routing decisions.

    Attributes:
        node_id: Unique identifier of the matched node.
        node_name: Human-readable name of the matched node.
        match_confidence: Matching confidence score (0.0 to 1.0).
        can_handle: Whether the node can process the file.
        required_capabilities: List of capabilities needed for processing.

    Example:
        ```python
        from uuid import uuid4

        class YamlHandlerMatch:
            node_id: UUID = uuid4()
            node_name: str = "yaml_processor"
            match_confidence: float = 0.95
            can_handle: bool = True
            required_capabilities: list[str] = ["yaml", "config"]

        match = YamlHandlerMatch()
        assert isinstance(match, ProtocolHandlerMatch)
        ```
    """

    node_id: UUID
    node_name: str
    match_confidence: float
    can_handle: bool
    required_capabilities: list[str]


@runtime_checkable
class ProtocolCanHandleResult(Protocol):
    """
    Protocol for handler capability determination results.

    Contains the outcome of checking whether a handler can process a
    specific file, including confidence scoring and reasoning for
    the decision. Used in handler selection workflows.

    Attributes:
        can_handle: Whether the handler can process the file.
        confidence: Confidence level of the determination (0.0 to 1.0).
        reason: Human-readable explanation of the decision.
        file_metadata: Metadata of the file being evaluated.

    Example:
        ```python
        class CanHandleMarkdown:
            can_handle: bool = True
            confidence: float = 0.99
            reason: str = "File extension .md matches markdown handler"
            file_metadata: ProtocolFileMetadata = metadata_impl

        result = CanHandleMarkdown()
        assert isinstance(result, ProtocolCanHandleResult)
        ```
    """

    can_handle: bool
    confidence: float
    reason: str
    file_metadata: ProtocolFileMetadata


@runtime_checkable
class ProtocolHandlerMetadata(Protocol):
    """
    Protocol for file handler/node metadata and configuration.

    Provides comprehensive metadata about a file handler including
    version information, supported file types, and processing requirements.
    Used for handler registration and discovery.

    Attributes:
        name: Handler name identifier.
        version: Semantic version of the handler.
        author: Creator/maintainer of the handler.
        description: Human-readable description of handler capabilities.
        supported_extensions: List of file extensions this handler processes.
        supported_filenames: List of specific filenames this handler processes.
        priority: Handler priority for selection (higher = preferred).
        requires_content_analysis: Whether content inspection is needed.

    Example:
        ```python
        class MarkdownHandlerMeta:
            name: str = "markdown_processor"
            version: ProtocolSemVer = semver_impl
            author: str = "ONEX Team"
            description: str = "Processes Markdown files"
            supported_extensions: list[str] = [".md", ".markdown"]
            supported_filenames: list[str] = ["README", "CHANGELOG"]
            priority: int = 100
            requires_content_analysis: bool = False

        meta = MarkdownHandlerMeta()
        assert isinstance(meta, ProtocolHandlerMetadata)
        ```
    """

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
    """
    Protocol for operation result data providing processing outcomes.

    Contains detailed data from completed operations including output
    locations, processed file lists, metrics, and warnings. This is an
    attribute-based protocol for data compatibility with storage systems.

    Attributes:
        output_path: Path to output file/directory, None if no output.
        processed_files: List of file paths that were processed.
        metrics: Dictionary of metric name to value mappings.
        warnings: List of warning messages generated during processing.

    Example:
        ```python
        class BatchProcessingData:
            output_path: str | None = "/output/batch_001"
            processed_files: list[str] = ["/src/a.py", "/src/b.py"]
            metrics: dict[str, float] = {"duration_ms": 125.5, "files": 2.0}
            warnings: list[str] = ["File c.py skipped: unsupported format"]

        data = BatchProcessingData()
        assert isinstance(data, ProtocolResultData)
        ```
    """

    output_path: str | None
    processed_files: list[str]
    metrics: dict[str, float]
    warnings: list[str]


@runtime_checkable
class ProtocolResult(Protocol):
    """
    Protocol for standardized ONEX operation results.

    Provides a consistent result structure for all ONEX operations
    including success status, messaging, detailed result data, error
    codes, and timestamps. Used as the standard return type for
    file processing and workflow operations.

    Attributes:
        success: Whether the operation completed successfully.
        message: Human-readable result message.
        result_data: Detailed operation data, None if operation failed early.
        error_code: Standardized error code if failed, None on success.
        timestamp: When the operation completed.

    Example:
        ```python
        class SuccessfulResult:
            success: bool = True
            message: str = "Processing completed successfully"
            result_data: ProtocolResultData | None = result_data_impl
            error_code: str | None = None
            timestamp: ProtocolDateTime = datetime_impl

        result = SuccessfulResult()
        assert isinstance(result, ProtocolResult)
        ```
    """

    success: bool
    message: str
    result_data: ProtocolResultData | None
    error_code: str | None
    timestamp: "ProtocolDateTime"


@runtime_checkable
class ProtocolResultOperations(Protocol):
    """
    Protocol for result operations providing service-level functionality.

    Defines method-based operations for result formatting, merging, and
    validation. This is a service protocol for implementing result
    management functionality across ONEX services.

    Attributes:
        format_result: Method to format a result for display or logging.
        merge_results: Async method to combine multiple results into one.
        validate_result: Async method to validate result integrity.

    Example:
        ```python
        class ResultService:
            def format_result(self, result: ProtocolResult) -> str:
                status = "OK" if result.success else "FAILED"
                return f"[{status}] {result.message}"

            async def merge_results(
                self, results: list[ProtocolResult]
            ) -> ProtocolResult:
                success = all(r.success for r in results)
                return MergedResultImpl(success=success, ...)

            async def validate_result(
                self, result: ProtocolResult
            ) -> bool:
                return result.success or result.error_code is not None

        service = ResultService()
        assert isinstance(service, ProtocolResultOperations)
        ```
    """

    def format_result(self, result: "ProtocolResult") -> str: ...

    async def merge_results(
        self, results: list["ProtocolResult"]
    ) -> ProtocolResult: ...

    async def validate_result(self, result: "ProtocolResult") -> bool: ...
