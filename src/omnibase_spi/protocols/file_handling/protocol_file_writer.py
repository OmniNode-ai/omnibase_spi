"""
Protocol for file writing operations.

This protocol defines the interface for writing files to various storage systems.
Implementations can write to filesystem, S3, memory, etc.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolFileWriter(Protocol):
    """
    Protocol for file writing operations in ONEX ecosystem.

    Defines the contract for file writing operations with support for
    multiple storage backends and atomic operations. Enables dependency
    injection and test isolation through protocol-based design.

    Key Features:
        - Single file writing with path flexibility
        - Batch file writing with atomic operations
        - Directory creation and management
        - File deletion operations
        - Protocol-based design for testability
        - Multiple storage backend support

    Supported Storage Backends:
        - FileSystemFileWriter: Local filesystem operations
        - MemoryFileWriter: In-memory file operations for testing
        - S3FileWriter: Amazon S3 cloud storage operations
        - FTPFileWriter: FTP server file operations
        - EncryptedFileWriter: Secure file writing with encryption

    Usage Example:
        ```python
        writer: ProtocolFileWriter = SomeFileWriter()

        # Write single file
        path = writer.write_file('config.yaml', yaml_content)

        # Write multiple files atomically
        files = [
            ('config/database.yaml', db_config),
            ('config/cache.yaml', cache_config),
            ('config/logging.yaml', log_config)
        ]
        written_paths = writer.write_files(files)

        # Ensure directory exists
        config_dir = writer.ensure_directory('config')

        # Delete file
        deleted = writer.delete_file('old_config.yaml')
        ```

    Integration Patterns:
        - Works with ONEX configuration management
        - Integrates with file processing pipelines
        - Supports dependency injection for testing
        - Compatible with validation and stamping workflows
        - Provides atomic operations for consistency
    """

    async def write_file(self, path: str, content: str) -> str:
        """
            ...
        Write content to a file.

        Args:
            path: str where to write the file
            content: Content to write

        Returns:
            str: Actual path where file was written

        Raises:
            IOError: If file cannot be written
        """
        ...

    async def write_files(self, files: list[tuple[str, str]]) -> list[str]: ...
    async def ensure_directory(self, path: str) -> str:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            path: Directory path to ensure exists

        Returns:
            str: The directory path

        Raises:
            IOError: If directory cannot be created
        """
        ...

    async def delete_file(self, path: str) -> bool:
        """
        Delete a file if it exists.

        Args:
            path: str to file to delete

        Returns:
            bool: True if file was deleted, False if it didn't exist

        Raises:
            IOError: If file exists but cannot be deleted
        """
        ...
