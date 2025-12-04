"""
Protocol interface for file I/O operations in ONEX ecosystem.

This protocol defines the interface for file I/O operations including YAML/JSON
processing, text/binary operations, and file system operations. Enables
in-memory/mock implementations for protocol-first testing and validation.

Domain: File Handling and I/O Operations
Author: ONEX Framework Team
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolFileIO(Protocol):
    """
    Protocol interface for file I/O operations in ONEX ecosystem.

    Defines the contract for file I/O operations including structured data formats
    (YAML/JSON), text processing, binary operations, and file system operations.
    Provides type-safe interfaces for both synchronous and asynchronous file handling.

    Key Features:
        - Structured data format support (YAML/JSON)
        - Text and binary file operations
        - File system operations (existence, listing, type checking)
        - Protocol-based design for testability
        - Mock implementation support for testing
        - Type-safe operation contracts

    Supported Operations:
        - YAML: read_yaml(), write_yaml()
        - JSON: read_json(), write_json()
        - Text: read_text(), write_text()
        - Binary: read_bytes(), write_bytes()
        - File System: exists(), is_file(), list_files()

    Usage Example:
        ```python
        file_io: ProtocolFileIO = SomeFileIOImplementation()

        # Read structured configuration
        config = file_io.read_yaml('config.yaml')
        data = file_io.read_json('data.json')

        # Write structured data
        file_io.write_yaml('output.yaml', processed_data)
        file_io.write_json('results.json', results)

        # File system operations
        if file_io.exists('important.txt'):
            content = file_io.read_text('important.txt')

        # List and filter files
        py_files = file_io.list_files('/project', pattern='*.py')
        ```

    Integration Patterns:
        - Works with ONEX configuration management
        - Integrates with file processing pipelines
        - Supports validation and stamping workflows
        - Provides mock implementations for testing
        - Compatible with both sync and async patterns
    """

    async def read_yaml(self, path: str) -> Any:
        """Read YAML content from a file path."""
        ...

    async def read_json(self, path: str) -> Any: ...
    async def write_yaml(self, path: str, data: Any) -> None:
        """Write YAML content to a file path."""
        ...

    async def write_json(self, path: str, data: Any) -> None:
        """Write JSON content to a file path."""
        ...

    async def exists(self, path: str) -> bool:
        """Check if a file exists."""
        ...

    async def is_file(self, path: str) -> bool:
        """Check if a path is a file."""
        ...

    async def list_files(
        self,
        directory: str,
        pattern: str | None = None,
    ) -> list[str]:
        """List files in a directory, optionally filtered by pattern."""
        ...

    async def read_text(self, path: str) -> str:
        """Read plain text content from a file path."""
        ...

    async def write_text(self, path: str, data: str) -> None: ...
    async def read_bytes(self, path: str) -> bytes:
        """Read binary content from a file path."""
        ...

    async def write_bytes(self, path: str, data: bytes) -> None:
        """Write binary content to a file path."""
        ...
