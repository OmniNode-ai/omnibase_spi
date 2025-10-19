# File Handling API Reference

## Overview

The ONEX file handling protocols provide comprehensive file processing capabilities with type detection, metadata stamping, directory traversal, and file I/O operations. These protocols enable sophisticated file management patterns with ONEX metadata integration and advanced file processing.

## 🏗️ Protocol Architecture

The file handling domain consists of **8 specialized protocols** that provide complete file management:

### File Reader Protocol

```python
from omnibase_spi.protocols.file_handling import ProtocolFileReader
from omnibase_spi.protocols.types.protocol_core_types import ContextValue

@runtime_checkable
class ProtocolFileReader(Protocol):
    """
    Protocol for file reading operations.

    Provides comprehensive file reading capabilities with
    streaming, chunking, and metadata extraction.

    Key Features:
        - File reading with streaming support
        - Chunked reading for large files
        - Metadata extraction and processing
        - File type detection and validation
        - Performance optimization
        - Error handling and recovery
    """

    async def read_file(
        self,
        file_path: str,
        encoding: str = "utf-8",
        chunk_size: int = 8192,
    ) -> ContextValue: ...

    async def read_file_chunked(
        self,
        file_path: str,
        chunk_size: int = 8192,
        encoding: str = "utf-8",
    ) -> AsyncIterator[bytes]: ...

    async def read_file_metadata(
        self, file_path: str
    ) -> ProtocolFileMetadata: ...

    async def read_file_lines(
        self,
        file_path: str,
        encoding: str = "utf-8",
        strip_newlines: bool = True,
    ) -> AsyncIterator[str]: ...

    async def read_binary_file(
        self, file_path: str
    ) -> bytes: ...

    async def read_file_with_offset(
        self,
        file_path: str,
        offset: int,
        length: int | None = None,
    ) -> bytes: ...

    async def get_file_size(self, file_path: str) -> int: ...

    async def get_file_checksum(
        self, file_path: str, algorithm: str = "sha256"
    ) -> str: ...
```

### File Writer Protocol

```python
@runtime_checkable
class ProtocolFileWriter(Protocol):
    """
    Protocol for file writing operations.

    Provides comprehensive file writing capabilities with
    atomic operations, streaming, and metadata management.

    Key Features:
        - Atomic file writing operations
        - Streaming write support
        - Metadata preservation and updating
        - File type validation
        - Performance optimization
        - Error handling and recovery
    """

    async def write_file(
        self,
        file_path: str,
        content: ContextValue,
        encoding: str = "utf-8",
        create_directories: bool = True,
    ) -> bool: ...

    async def write_file_atomic(
        self,
        file_path: str,
        content: ContextValue,
        temp_suffix: str = ".tmp",
    ) -> bool: ...

    async def write_file_chunked(
        self,
        file_path: str,
        content_stream: AsyncIterator[bytes],
        create_directories: bool = True,
    ) -> bool: ...

    async def append_to_file(
        self,
        file_path: str,
        content: ContextValue,
        encoding: str = "utf-8",
    ) -> bool: ...

    async def write_binary_file(
        self,
        file_path: str,
        content: bytes,
        create_directories: bool = True,
    ) -> bool: ...

    async def write_file_with_metadata(
        self,
        file_path: str,
        content: ContextValue,
        metadata: ProtocolFileMetadata,
    ) -> bool: ...

    async def create_directory(
        self, directory_path: str, parents: bool = True
    ) -> bool: ...

    async def set_file_permissions(
        self, file_path: str, permissions: int
    ) -> bool: ...
```

### File Type Handler Protocol

```python
@runtime_checkable
class ProtocolFileTypeHandler(Protocol):
    """
    Protocol for file type handling operations.

    Provides file type detection, processing, and validation
    with support for multiple file formats and MIME types.

    Key Features:
        - File type detection and validation
        - MIME type identification
        - File format processing
        - Content validation
        - Metadata extraction
        - Performance optimization
    """

    async def detect_file_type(
        self, file_path: str
    ) -> ProtocolFileTypeInfo: ...

    async def detect_file_type_from_content(
        self, content: bytes
    ) -> ProtocolFileTypeInfo: ...

    async def validate_file_type(
        self, file_path: str, expected_type: str
    ) -> bool: ...

    async def get_mime_type(self, file_path: str) -> str: ...

    async def get_file_extension(self, file_path: str) -> str: ...

    async def is_text_file(self, file_path: str) -> bool: ...

    async def is_binary_file(self, file_path: str) -> bool: ...

    async def get_file_encoding(
        self, file_path: str
    ) -> str | None: ...

    async def process_file_by_type(
        self, file_path: str, processing_options: dict[str, Any]
    ) -> ProtocolFileProcessingResult: ...
```

### File Type Handler Registry Protocol

```python
@runtime_checkable
class ProtocolFileTypeHandlerRegistry(Protocol):
    """
    Protocol for file type handler registry operations.

    Manages file type handlers with registration,
    discovery, and handler management.

    Key Features:
        - Handler registration and discovery
        - File type to handler mapping
        - Handler lifecycle management
        - Performance monitoring
        - Error handling and recovery
    """

    async def register_handler(
        self,
        file_type: str,
        handler: ProtocolFileTypeHandler,
        priority: int = 0,
    ) -> bool: ...

    async def unregister_handler(
        self, file_type: str, handler_id: str
    ) -> bool: ...

    async def get_handler(
        self, file_type: str
    ) -> ProtocolFileTypeHandler | None: ...

    async def get_all_handlers(
        self,
    ) -> dict[str, list[ProtocolFileTypeHandler]]: ...

    async def get_supported_types(
        self,
    ) -> list[str]: ...

    async def get_handler_metrics(
        self, handler_id: str
    ) -> ProtocolHandlerMetrics: ...

    async def update_handler_priority(
        self, file_type: str, handler_id: str, priority: int
    ) -> bool: ...
```

### Directory Traverser Protocol

```python
@runtime_checkable
class ProtocolDirectoryTraverser(Protocol):
    """
    Protocol for directory traversal operations.

    Provides comprehensive directory traversal with
    filtering, recursion control, and performance optimization.

    Key Features:
        - Recursive directory traversal
        - File and directory filtering
        - Performance optimization
        - Memory-efficient traversal
        - Error handling and recovery
        - Metadata collection
    """

    async def traverse_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        include_files: bool = True,
        include_directories: bool = True,
        filter_pattern: str | None = None,
    ) -> AsyncIterator[ProtocolFileSystemItem]: ...

    async def get_directory_contents(
        self,
        directory_path: str,
        recursive: bool = False,
        filter_pattern: str | None = None,
    ) -> list[ProtocolFileSystemItem]: ...

    async def find_files(
        self,
        directory_path: str,
        pattern: str,
        recursive: bool = True,
    ) -> list[str]: ...

    async def get_directory_size(
        self, directory_path: str
    ) -> int: ...

    async def get_directory_metadata(
        self, directory_path: str
    ) -> ProtocolDirectoryMetadata: ...

    async def count_files(
        self,
        directory_path: str,
        recursive: bool = True,
        filter_pattern: str | None = None,
    ) -> int: ...

    async def get_directory_tree(
        self, directory_path: str
    ) -> ProtocolDirectoryTree: ...
```

### File Discovery Source Protocol

```python
@runtime_checkable
class ProtocolFileDiscoverySource(Protocol):
    """
    Protocol for file discovery source operations.

    Provides file discovery capabilities with
    multiple source types and discovery strategies.

    Key Features:
        - Multiple discovery sources
        - Discovery strategy management
        - File filtering and validation
        - Performance optimization
        - Error handling and recovery
        - Metadata collection
    """

    async def discover_files(
        self,
        source_config: ProtocolDiscoverySourceConfig,
        discovery_options: ProtocolDiscoveryOptions,
    ) -> list[ProtocolDiscoveredFile]: ...

    async def register_discovery_source(
        self,
        source_name: str,
        source_type: LiteralDiscoverySourceType,
        config: dict[str, Any],
    ) -> bool: ...

    async def unregister_discovery_source(
        self, source_name: str
    ) -> bool: ...

    async def get_discovery_sources(
        self,
    ) -> list[ProtocolDiscoverySourceInfo]: ...

    async def get_discovery_metrics(
        self, source_name: str
    ) -> ProtocolDiscoveryMetrics: ...

    async def validate_discovery_source(
        self, source_name: str
    ) -> ProtocolValidationResult: ...

    async def test_discovery_connection(
        self, source_name: str
    ) -> bool: ...
```

### File Processing Protocol

```python
@runtime_checkable
class ProtocolFileProcessing(Protocol):
    """
    Protocol for file processing operations.

    Provides comprehensive file processing with
    transformation, validation, and metadata management.

    Key Features:
        - File transformation and processing
        - Content validation and sanitization
        - Metadata extraction and management
        - Performance optimization
        - Error handling and recovery
        - Processing pipeline support
    """

    async def process_file(
        self,
        file_path: str,
        processing_pipeline: list[ProtocolFileProcessor],
        options: ProtocolProcessingOptions,
    ) -> ProtocolFileProcessingResult: ...

    async def transform_file(
        self,
        file_path: str,
        transformation: ProtocolFileTransformation,
        output_path: str,
    ) -> bool: ...

    async def validate_file_content(
        self,
        file_path: str,
        validation_rules: list[ProtocolValidationRule],
    ) -> ProtocolValidationResult: ...

    async def extract_metadata(
        self, file_path: str
    ) -> ProtocolFileMetadata: ...

    async def sanitize_file_content(
        self,
        file_path: str,
        sanitization_rules: list[ProtocolSanitizationRule],
    ) -> bool: ...

    async def get_processing_metrics(
        self, processing_id: str
    ) -> ProtocolProcessingMetrics: ...

    async def cancel_processing(
        self, processing_id: str
    ) -> bool: ...
```

### File I/O Protocol

```python
@runtime_checkable
class ProtocolFileIO(Protocol):
    """
    Protocol for file I/O operations.

    Provides comprehensive file I/O capabilities with
    streaming, buffering, and performance optimization.

    Key Features:
        - High-performance file I/O
        - Streaming and buffering
        - Memory optimization
        - Error handling and recovery
        - Performance monitoring
        - Cross-platform compatibility
    """

    async def open_file(
        self,
        file_path: str,
        mode: LiteralFileMode,
        encoding: str | None = None,
    ) -> ProtocolFileHandle: ...

    async def close_file(self, file_handle: ProtocolFileHandle) -> bool: ...

    async def read_from_file(
        self,
        file_handle: ProtocolFileHandle,
        size: int | None = None,
    ) -> bytes: ...

    async def write_to_file(
        self,
        file_handle: ProtocolFileHandle,
        data: bytes,
    ) -> int: ...

    async def seek_in_file(
        self,
        file_handle: ProtocolFileHandle,
        position: int,
        whence: LiteralSeekWhence = "start",
    ) -> int: ...

    async def get_file_position(
        self, file_handle: ProtocolFileHandle
    ) -> int: ...

    async def flush_file(
        self, file_handle: ProtocolFileHandle
    ) -> bool: ...

    async def get_file_handle_info(
        self, file_handle: ProtocolFileHandle
    ) -> ProtocolFileHandleInfo: ...
```

## 🔧 Type Definitions

### File Mode Types

```python
LiteralFileMode = Literal["r", "w", "a", "x", "rb", "wb", "ab", "xb"]
"""
File opening modes.

Values:
    r: Read mode (text)
    w: Write mode (text)
    a: Append mode (text)
    x: Exclusive creation mode (text)
    rb: Read mode (binary)
    wb: Write mode (binary)
    ab: Append mode (binary)
    xb: Exclusive creation mode (binary)
"""

LiteralSeekWhence = Literal["start", "current", "end"]
"""
File seek reference points.

Values:
    start: Seek from beginning of file
    current: Seek from current position
    end: Seek from end of file
"""

LiteralDiscoverySourceType = Literal["local", "remote", "cloud", "database"]
"""
File discovery source types.

Values:
    local: Local file system
    remote: Remote file system (FTP, SFTP)
    cloud: Cloud storage (S3, GCS, Azure)
    database: Database file storage
"""
```

## 🚀 Usage Examples

### File Reading Operations

```python
from omnibase_spi.protocols.file_handling import ProtocolFileReader

# Initialize file reader
file_reader: ProtocolFileReader = get_file_reader()

# Read entire file
content = await file_reader.read_file(
    file_path="/path/to/document.txt",
    encoding="utf-8"
)
print(f"File content: {content}")

# Read file in chunks
async for chunk in file_reader.read_file_chunked(
    file_path="/path/to/large-file.txt",
    chunk_size=4096
):
    print(f"Read chunk: {len(chunk)} bytes")

# Read file metadata
metadata = await file_reader.read_file_metadata("/path/to/document.txt")
print(f"File size: {metadata.size} bytes")
print(f"Created: {metadata.created_at}")
print(f"Modified: {metadata.modified_at}")

# Read file lines
async for line in file_reader.read_file_lines("/path/to/logfile.txt"):
    print(f"Line: {line}")

# Get file checksum
checksum = await file_reader.get_file_checksum(
    "/path/to/document.txt",
    algorithm="sha256"
)
print(f"File checksum: {checksum}")
```

### File Writing Operations

```python
from omnibase_spi.protocols.file_handling import ProtocolFileWriter

# Initialize file writer
file_writer: ProtocolFileWriter = get_file_writer()

# Write file content
await file_writer.write_file(
    file_path="/path/to/output.txt",
    content="Hello, World!",
    encoding="utf-8",
    create_directories=True
)

# Atomic file writing
await file_writer.write_file_atomic(
    file_path="/path/to/important.txt",
    content="Critical data",
    temp_suffix=".tmp"
)

# Write binary file
binary_data = b"\x89PNG\r\n\x1a\n"  # PNG header
await file_writer.write_binary_file(
    file_path="/path/to/image.png",
    content=binary_data
)

# Write with metadata
await file_writer.write_file_with_metadata(
    file_path="/path/to/document.txt",
    content="Document content",
    metadata=ProtocolFileMetadata(
        author="John Doe",
        created_at=datetime.now(),
        tags=["document", "important"]
    )
)

# Set file permissions
await file_writer.set_file_permissions(
    file_path="/path/to/script.sh",
    permissions=0o755
)
```

### File Type Detection

```python
from omnibase_spi.protocols.file_handling import ProtocolFileTypeHandler

# Initialize file type handler
file_type_handler: ProtocolFileTypeHandler = get_file_type_handler()

# Detect file type
file_type_info = await file_type_handler.detect_file_type(
    "/path/to/document.pdf"
)
print(f"File type: {file_type_info.type}")
print(f"MIME type: {file_type_info.mime_type}")
print(f"Extension: {file_type_info.extension}")

# Detect from content
with open("/path/to/unknown", "rb") as f:
    content = f.read(1024)  # Read first 1KB
    type_info = await file_type_handler.detect_file_type_from_content(content)
    print(f"Detected type: {type_info.type}")

# Validate file type
is_valid = await file_type_handler.validate_file_type(
    "/path/to/image.jpg",
    expected_type="image"
)
print(f"File type valid: {is_valid}")

# Check if text file
is_text = await file_type_handler.is_text_file("/path/to/document.txt")
print(f"Is text file: {is_text}")

# Get file encoding
encoding = await file_type_handler.get_file_encoding("/path/to/document.txt")
print(f"File encoding: {encoding}")
```

### Directory Traversal

```python
from omnibase_spi.protocols.file_handling import ProtocolDirectoryTraverser

# Initialize directory traverser
traverser: ProtocolDirectoryTraverser = get_directory_traverser()

# Traverse directory
async for item in traverser.traverse_directory(
    directory_path="/path/to/project",
    recursive=True,
    include_files=True,
    include_directories=True,
    filter_pattern="*.py"
):
    print(f"Found: {item.path} ({item.type})")

# Get directory contents
contents = await traverser.get_directory_contents(
    directory_path="/path/to/project",
    recursive=False
)
print(f"Directory contents: {len(contents)} items")

# Find specific files
python_files = await traverser.find_files(
    directory_path="/path/to/project",
    pattern="*.py",
    recursive=True
)
print(f"Python files: {python_files}")

# Get directory size
total_size = await traverser.get_directory_size("/path/to/project")
print(f"Total size: {total_size} bytes")

# Count files
file_count = await traverser.count_files(
    directory_path="/path/to/project",
    recursive=True,
    filter_pattern="*.py"
)
print(f"Python files count: {file_count}")
```

### File Processing

```python
from omnibase_spi.protocols.file_handling import ProtocolFileProcessing

# Initialize file processor
processor: ProtocolFileProcessing = get_file_processor()

# Process file with pipeline
processing_result = await processor.process_file(
    file_path="/path/to/document.txt",
    processing_pipeline=[
        ProtocolFileProcessor("text_extraction"),
        ProtocolFileProcessor("metadata_extraction"),
        ProtocolFileProcessor("content_validation")
    ],
    options=ProtocolProcessingOptions(
        output_format="json",
        preserve_original=True
    )
)

print(f"Processing result: {processing_result.success}")
print(f"Output file: {processing_result.output_path}")

# Transform file
await processor.transform_file(
    file_path="/path/to/document.txt",
    transformation=ProtocolFileTransformation(
        type="text_to_markdown",
        options={"heading_level": 2}
    ),
    output_path="/path/to/document.md"
)

# Validate file content
validation_result = await processor.validate_file_content(
    file_path="/path/to/document.txt",
    validation_rules=[
        ProtocolValidationRule("min_length", 100),
        ProtocolValidationRule("max_length", 10000),
        ProtocolValidationRule("encoding", "utf-8")
    ]
)

print(f"Validation passed: {validation_result.valid}")
if not validation_result.valid:
    print(f"Validation errors: {validation_result.errors}")
```

### File I/O Operations

```python
from omnibase_spi.protocols.file_handling import ProtocolFileIO

# Initialize file I/O
file_io: ProtocolFileIO = get_file_io()

# Open file for reading
file_handle = await file_io.open_file(
    file_path="/path/to/document.txt",
    mode="r",
    encoding="utf-8"
)

# Read from file
data = await file_io.read_from_file(file_handle, size=1024)
print(f"Read {len(data)} bytes")

# Seek to position
position = await file_io.seek_in_file(file_handle, 512, "start")
print(f"Current position: {position}")

# Get file position
current_pos = await file_io.get_file_position(file_handle)
print(f"Current position: {current_pos}")

# Close file
await file_io.close_file(file_handle)

# Open file for writing
write_handle = await file_io.open_file(
    file_path="/path/to/output.txt",
    mode="w",
    encoding="utf-8"
)

# Write to file
bytes_written = await file_io.write_to_file(
    write_handle,
    b"Hello, World!"
)
print(f"Wrote {bytes_written} bytes")

# Flush file
await file_io.flush_file(write_handle)

# Close file
await file_io.close_file(write_handle)
```

## 🔍 Implementation Notes

### File Type Handler Registry

Advanced file type management:

```python
# Register custom file type handler
await file_type_registry.register_handler(
    file_type="custom",
    handler=custom_handler,
    priority=10
)

# Get handler for specific type
handler = await file_type_registry.get_handler("pdf")
if handler:
    result = await handler.process_file_by_type(
        file_path, {"extract_text": True}
    )
```

### Performance Optimization

Efficient file processing patterns:

```python
# Stream large files
async for chunk in file_reader.read_file_chunked(
    file_path, chunk_size=8192
):
    # Process chunk
    processed_chunk = process_chunk(chunk)
    await file_writer.write_file_chunked(
        output_path, processed_chunk
    )
```

### Error Handling

Robust error handling patterns:

```python
try:
    result = await file_processor.process_file(
        file_path, processing_pipeline, options
    )
except FileProcessingError as e:
    print(f"Processing failed: {e}")
    # Handle error appropriately
```

## 📊 Protocol Statistics

- **Total Protocols**: 8 file handling protocols
- **File Operations**: Reading, writing, and processing
- **Type Detection**: MIME type and file format detection
- **Directory Traversal**: Recursive and filtered traversal
- **File Discovery**: Multiple source type support
- **Performance**: Streaming, chunking, and optimization
- **Metadata**: Comprehensive file metadata management

---

*This API reference is automatically generated from protocol definitions and maintained alongside the codebase.*
