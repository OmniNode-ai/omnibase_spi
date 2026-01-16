"""
File handling protocol types for ONEX SPI interfaces.

Domain: File content, metadata, and block protocols

Note: Result and handler protocols have been moved to protocol_file_result_types.py
and are re-exported here for backward compatibility.
"""

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ProtocolSemVer

LiteralFileOperation = Literal["read", "write", "append", "delete", "move", "copy"]
LiteralFileStatus = Literal["exists", "missing", "locked", "corrupted", "accessible"]


@runtime_checkable
class ProtocolFileContent(Protocol):
    """
    Protocol for file content values supporting validation and serialization.

    Defines the base interface for all file content types in ONEX, providing
    standardized validation and serialization capabilities. This protocol
    enables type-safe file operations across different content formats.

    Attributes:
        validate_for_file: Async method to validate content for file storage.
        serialize_for_file: Method to serialize content to dictionary format.

    Example:
        ```python
        class TextFileContent:
            async def validate_for_file(self) -> bool:
                return len(self.content) > 0

            def serialize_for_file(self) -> dict[str, object]:
                return {"content": self.content, "type": "text"}

        content = TextFileContent()
        assert isinstance(content, ProtocolFileContent)
        ```
    """

    async def validate_for_file(self) -> bool: ...

    def serialize_for_file(self) -> dict[str, object]: ...


@runtime_checkable
class ProtocolStringFileContent(ProtocolFileContent, Protocol):
    """
    Protocol for string-based file content representing text files.

    Extends ProtocolFileContent to provide specialized handling for text-based
    file content. Used throughout ONEX for processing text files, configuration
    files, source code, and other string-serializable content.

    Attributes:
        value: The string content of the text file.

    Example:
        ```python
        class ConfigFileContent:
            value: str = "key=value\\nother=data"

            async def validate_for_file(self) -> bool:
                return bool(self.value)

            def serialize_for_file(self) -> dict[str, object]:
                return {"value": self.value, "encoding": "utf-8"}

        config = ConfigFileContent()
        assert isinstance(config, ProtocolStringFileContent)
        ```
    """

    value: str


@runtime_checkable
class ProtocolBinaryFileContent(ProtocolFileContent, Protocol):
    """
    Protocol for binary file content representing non-text files.

    Extends ProtocolFileContent to provide specialized handling for binary
    file content. Used throughout ONEX for processing images, compiled files,
    archives, and other binary data formats.

    Attributes:
        value: The raw bytes content of the binary file.

    Example:
        ```python
        class ImageFileContent:
            value: bytes = b"\\x89PNG\\r\\n\\x1a\\n..."

            async def validate_for_file(self) -> bool:
                return len(self.value) > 0

            def serialize_for_file(self) -> dict[str, object]:
                import base64
                return {"value": base64.b64encode(self.value).decode()}

        image = ImageFileContent()
        assert isinstance(image, ProtocolBinaryFileContent)
        ```
    """

    value: bytes


FileContent = ProtocolFileContent


@runtime_checkable
class ProtocolFileMetadata(Protocol):
    """
    Protocol for file metadata providing essential file system information.

    Defines the standard metadata structure for files in ONEX, supporting
    file management, caching, and synchronization operations. This is an
    attribute-based protocol for data compatibility with storage systems.

    Attributes:
        size: File size in bytes.
        mime_type: MIME type string (e.g., "text/plain", "application/json").
        encoding: Character encoding for text files (e.g., "utf-8"), None for binary.
        created_at: Unix timestamp of file creation.
        modified_at: Unix timestamp of last modification.

    Example:
        ```python
        class FileMetadataImpl:
            size: int = 1024
            mime_type: str = "text/plain"
            encoding: str | None = "utf-8"
            created_at: float = 1699900000.0
            modified_at: float = 1699900100.0

        metadata = FileMetadataImpl()
        assert isinstance(metadata, ProtocolFileMetadata)
        ```
    """

    size: int
    mime_type: str
    encoding: str | None
    created_at: float
    modified_at: float


@runtime_checkable
class ProtocolFileInfo(Protocol):
    """
    Protocol for comprehensive file information objects.

    Provides complete file information including path, size, type, and
    current status. Used for file discovery, listing operations, and
    file system traversal throughout ONEX services.

    Attributes:
        file_path: Absolute or relative path to the file.
        file_size: File size in bytes.
        file_type: File type classification (e.g., "document", "image", "code").
        mime_type: MIME type string for content type identification.
        last_modified: Unix timestamp of last modification.
        status: Current file status from LiteralFileStatus.

    Example:
        ```python
        class FileInfoImpl:
            file_path: str = "/data/config.yaml"
            file_size: int = 2048
            file_type: str = "configuration"
            mime_type: str = "application/yaml"
            last_modified: float = 1699900000.0
            status: LiteralFileStatus = "exists"

        info = FileInfoImpl()
        assert isinstance(info, ProtocolFileInfo)
        ```
    """

    file_path: str
    file_size: int
    file_type: str
    mime_type: str
    last_modified: float
    status: LiteralFileStatus


@runtime_checkable
class ProtocolFileContentObject(Protocol):
    """
    Protocol for file content objects combining content with metadata.

    Represents a complete file with its content and associated metadata,
    used for file read/write operations, content validation, and
    integrity verification throughout ONEX file handling services.

    Attributes:
        file_path: Path to the file being represented.
        content: The actual file content (text or binary).
        encoding: Character encoding for text files, None for binary.
        content_hash: Hash of content for integrity verification.
        is_binary: True if content is binary, False for text.

    Example:
        ```python
        class FileContentObjectImpl:
            file_path: str = "/data/document.txt"
            content: FileContent = StringContentImpl("Hello, World!")
            encoding: str | None = "utf-8"
            content_hash: str = "a591a6d40bf420..."
            is_binary: bool = False

        obj = FileContentObjectImpl()
        assert isinstance(obj, ProtocolFileContentObject)
        ```
    """

    file_path: str
    content: FileContent
    encoding: str | None
    content_hash: str
    is_binary: bool


@runtime_checkable
class ProtocolFileFilter(Protocol):
    """
    Protocol for file filtering criteria in search and discovery operations.

    Defines comprehensive filtering options for file system operations,
    enabling targeted file searches based on extensions, size ranges,
    and modification timestamps.

    Attributes:
        include_extensions: List of extensions to include (e.g., [".py", ".txt"]).
        exclude_extensions: List of extensions to exclude from results.
        min_size: Minimum file size in bytes (None for no minimum).
        max_size: Maximum file size in bytes (None for no maximum).
        modified_after: Include files modified after this timestamp.
        modified_before: Include files modified before this timestamp.

    Example:
        ```python
        class PythonFileFilter:
            include_extensions: list[str] = [".py", ".pyi"]
            exclude_extensions: list[str] = ["__pycache__"]
            min_size: int | None = 1
            max_size: int | None = 1_000_000
            modified_after: float | None = 1699000000.0
            modified_before: float | None = None

        filter = PythonFileFilter()
        assert isinstance(filter, ProtocolFileFilter)
        ```
    """

    include_extensions: list[str]
    exclude_extensions: list[str]
    min_size: int | None
    max_size: int | None
    modified_after: float | None
    modified_before: float | None


@runtime_checkable
class ProtocolExtractedBlock(Protocol):
    """
    Protocol for extracted block data from file content.

    Represents a discrete section of content extracted from a file,
    including location information and block type classification.
    Used for code extraction, content parsing, and structured
    document processing.

    Attributes:
        content: The extracted text content of the block.
        file_metadata: Metadata of the source file.
        block_type: Type classification (e.g., "function", "class", "comment").
        start_line: Starting line number (1-indexed), None if unknown.
        end_line: Ending line number (1-indexed), None if unknown.
        path: File path from which the block was extracted.

    Example:
        ```python
        class FunctionBlock:
            content: str = "def example(): pass"
            file_metadata: ProtocolFileMetadata = file_meta_impl
            block_type: str = "function"
            start_line: int | None = 10
            end_line: int | None = 15
            path: str = "/src/module.py"

        block = FunctionBlock()
        assert isinstance(block, ProtocolExtractedBlock)
        ```
    """

    content: str
    file_metadata: ProtocolFileMetadata
    block_type: str
    start_line: int | None
    end_line: int | None
    path: str


@runtime_checkable
class ProtocolSerializedBlock(Protocol):
    """
    Protocol for serialized block data ready for storage or transmission.

    Represents block content that has been serialized to a string format,
    including format information and version tracking for compatibility.
    Used for block persistence, caching, and inter-service communication.

    Attributes:
        serialized_data: The serialized string representation of the block.
        serialization_format: Serialization format (e.g., "json", "yaml", "msgpack").
        version: Semantic version of the serialization schema.
        file_metadata: Metadata of the original source file.

    Example:
        ```python
        class JsonSerializedBlock:
            serialized_data: str = '{"type": "function", "name": "example"}'
            serialization_format: str = "json"
            version: ProtocolSemVer = semver_impl
            file_metadata: ProtocolFileMetadata = file_meta_impl

        block = JsonSerializedBlock()
        assert isinstance(block, ProtocolSerializedBlock)
        ```
    """

    serialized_data: str
    serialization_format: str
    version: "ProtocolSemVer"
    file_metadata: ProtocolFileMetadata


@runtime_checkable
class ProtocolFileMetadataOperations(Protocol):
    """
    Protocol for file metadata operations providing service-level functionality.

    Defines method-based operations for metadata validation, serialization,
    and comparison. This is a service protocol for implementing metadata
    management functionality across ONEX file handling services.

    Attributes:
        validate_metadata: Async method to validate metadata structure.
        serialize_metadata: Async method to serialize metadata to string.
        compare_metadata: Async method to compare two metadata objects.

    Example:
        ```python
        class MetadataService:
            async def validate_metadata(
                self, metadata: ProtocolFileMetadata
            ) -> bool:
                return metadata.size >= 0

            async def serialize_metadata(
                self, metadata: ProtocolFileMetadata
            ) -> str:
                return json.dumps({"size": metadata.size})

            async def compare_metadata(
                self, meta1: ProtocolFileMetadata, meta2: ProtocolFileMetadata
            ) -> bool:
                return meta1.content_hash == meta2.content_hash

        service = MetadataService()
        assert isinstance(service, ProtocolFileMetadataOperations)
        ```
    """

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
    ProtocolProcessingResult,
    ProtocolResult,
    ProtocolResultData,
    ProtocolResultOperations,
)

__all__ = [
    "FileContent",
    # Literals
    "LiteralFileOperation",
    "LiteralFileStatus",
    # Re-exported from protocol_file_result_types
    "ProcessingStatus",
    "ProtocolBinaryFileContent",
    "ProtocolCanHandleResult",
    "ProtocolExtractedBlock",
    # Protocols defined in this module
    "ProtocolFileContent",
    "ProtocolFileContentObject",
    "ProtocolFileFilter",
    "ProtocolFileInfo",
    "ProtocolFileMetadata",
    "ProtocolFileMetadataOperations",
    "ProtocolFileTypeResult",
    "ProtocolHandlerMatch",
    "ProtocolHandlerMetadata",
    "ProtocolProcessingResult",
    "ProtocolResult",
    "ProtocolResultData",
    "ProtocolResultOperations",
    "ProtocolSerializedBlock",
    "ProtocolStringFileContent",
]
