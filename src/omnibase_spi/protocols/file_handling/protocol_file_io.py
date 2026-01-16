"""
Protocol interface for file I/O operations in ONEX ecosystem.

This protocol defines the interface for file I/O operations including YAML/JSON
processing, text/binary operations, and file system operations. Enables
in-memory/mock implementations for protocol-first testing and validation.

Domain: File Handling and I/O Operations
Author: ONEX Framework Team
"""

from typing import Protocol, runtime_checkable

from omnibase_core.types import JsonType


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

    async def read_yaml(self, path: str) -> JsonType:
        """Read and parse YAML content from a file.

        Args:
            path: The file path to read YAML content from.

        Returns:
            Parsed YAML content as a JSON-compatible type (dict, list, or scalar).

        Raises:
            FileNotFoundError: When the specified file does not exist.
            ValueError: When the file contains invalid YAML syntax.
            PermissionError: When read access to the file is denied.
            OSError: When an I/O error occurs during the read operation.
        """
        ...

    async def read_json(self, path: str) -> JsonType:
        """Read and parse JSON content from a file.

        Args:
            path: The file path to read JSON content from.

        Returns:
            Parsed JSON content as a JSON-compatible type (dict, list, or scalar).

        Raises:
            FileNotFoundError: When the specified file does not exist.
            ValueError: When the file contains invalid JSON syntax.
            PermissionError: When read access to the file is denied.
            OSError: When an I/O error occurs during the read operation.
        """
        ...

    async def write_yaml(self, path: str, data: JsonType) -> None:
        """Write data to a file in YAML format.

        Args:
            path: The file path to write YAML content to.
            data: The data to serialize and write as YAML.

        Returns:
            None

        Raises:
            PermissionError: When write access to the file is denied.
            TypeError: When the data cannot be serialized to YAML.
            OSError: When the file cannot be written due to I/O errors.
        """
        ...

    async def write_json(self, path: str, data: JsonType) -> None:
        """Write data to a file in JSON format.

        Args:
            path: The file path to write JSON content to.
            data: The data to serialize and write as JSON.

        Returns:
            None

        Raises:
            PermissionError: When write access to the file is denied.
            TypeError: When the data cannot be serialized to JSON.
            OSError: When the file cannot be written due to I/O errors.
        """
        ...

    async def exists(self, path: str) -> bool:
        """Check if a file or directory exists at the given path.

        Args:
            path: The file or directory path to check.

        Returns:
            True if the path exists, False otherwise.

        Raises:
            PermissionError: When the path cannot be accessed due to permissions.
            OSError: When an I/O error occurs during the check.
        """
        ...

    async def is_file(self, path: str) -> bool:
        """Check if the path points to a regular file.

        Args:
            path: The path to check.

        Returns:
            True if the path is a regular file, False if it is a directory
            or does not exist.

        Raises:
            PermissionError: When the path cannot be accessed due to permissions.
            OSError: When an I/O error occurs during the check.
        """
        ...

    async def list_files(
        self,
        directory: str,
        pattern: str | None = None,
    ) -> list[str]:
        """List files in a directory, optionally filtered by a glob pattern.

        Args:
            directory: The directory path to list files from.
            pattern: Optional glob pattern to filter files (e.g., '*.py', '*.yaml').

        Returns:
            List of file paths matching the criteria.

        Raises:
            FileNotFoundError: When the specified directory does not exist.
            NotADirectoryError: When the path is not a directory.
            PermissionError: When the directory cannot be accessed due to permissions.
            OSError: When an I/O error occurs during the listing operation.
        """
        ...

    async def read_text(self, path: str) -> str:
        """Read plain text content from a file.

        Args:
            path: The file path to read text content from.

        Returns:
            The file content as a string.

        Raises:
            FileNotFoundError: When the specified file does not exist.
            PermissionError: When read access to the file is denied.
            UnicodeDecodeError: When the file cannot be decoded as text.
            OSError: When an I/O error occurs during the read operation.
        """
        ...

    async def write_text(self, path: str, data: str) -> None:
        """Write plain text content to a file.

        Args:
            path: The file path to write text content to.
            data: The text content to write.

        Returns:
            None

        Raises:
            PermissionError: When write access to the file is denied.
            OSError: When the file cannot be written due to I/O errors.
        """
        ...

    async def read_bytes(self, path: str) -> bytes:
        """Read binary content from a file.

        Args:
            path: The file path to read binary content from.

        Returns:
            The file content as bytes.

        Raises:
            FileNotFoundError: When the specified file does not exist.
            PermissionError: When read access to the file is denied.
            OSError: When an I/O error occurs during the read operation.
        """
        ...

    async def write_bytes(self, path: str, data: bytes) -> None:
        """Write binary content to a file.

        Args:
            path: The file path to write binary content to.
            data: The binary content to write.

        Returns:
            None

        Raises:
            PermissionError: When write access to the file is denied.
            OSError: When the file cannot be written due to I/O errors.
        """
        ...
