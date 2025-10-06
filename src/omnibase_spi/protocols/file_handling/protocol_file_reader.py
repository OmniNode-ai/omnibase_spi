"""
Protocol for file reading operations.

This protocol enables dependency injection for file I/O operations,
allowing for easy mocking in tests and alternative implementations.
"""

from typing import Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class ProtocolFileReader(Protocol):
    """
    Protocol for file reading operations in ONEX ecosystem.

    Defines the contract for file reading operations with support for
    multiple data formats and storage backends. Enables dependency
    injection and test isolation through protocol-based design.

    Key Features:
        - Text file reading with encoding support
        - YAML file parsing with type conversion
        - File existence checking
        - Protocol-based design for testability
        - Multiple backend support (filesystem, remote, etc.)

    Supported Implementation Patterns:
        - FileSystemFileReader: Direct filesystem access
        - MockFileReader: Test isolation with predefined content
        - RemoteFileReader: Cloud storage (S3, HTTP, etc.)
        - CachedFileReader: Performance optimization through caching
        - SecureFileReader: Encrypted file access

    Usage Example:
        ```python
        from typing import Protocol, runtime_checkable

        reader: ProtocolFileReader = SomeFileReader()

        # Read text content
        content = await reader.read_text('config.yaml')

        # Read and parse YAML with type conversion
        @runtime_checkable
        class ProtocolConfig(Protocol):
            name: str
            version: str

        config = await reader.read_yaml('config.yaml', ProtocolConfig)

        # Check file existence
        if await reader.exists('important.txt'):
            content = await reader.read_text('important.txt')
        ```

    Integration Patterns:
        - Works with ONEX configuration management
        - Integrates with file processing pipelines
        - Supports dependency injection for testing
        - Compatible with async processing patterns
    """

    async def read_text(self, path: str) -> str:
        """
        Read text content from a file path.

        Performs text file reading with appropriate encoding handling
        and error management for missing or inaccessible files.

        Args:
            path: File path to read (relative or absolute)

        Returns:
            Text content of the file as string

        Raises:
            FileNotFoundError: If file does not exist
            PermissionError: If file cannot be accessed
            UnicodeDecodeError: If file encoding is not supported

        Example:
            ```python
            content = await reader.read_text('config/settings.yaml')
            print(f"Config content: {content}")
            ```
        """
        ...

    async def read_yaml(self, path: str, data_class: type[T]) -> T:
        """
        Read YAML content and parse into specified data class.

        Performs YAML file parsing with automatic type conversion
        to the specified data class structure.

        Args:
            path: YAML file path to read
            data_class: Target data class for type conversion

        Returns:
            Parsed data as instance of specified data class

        Raises:
            FileNotFoundError: If YAML file does not exist
            yaml.YAMLError: If YAML parsing fails
            TypeError: If data conversion fails

        Example:
            ```python
            from typing import Protocol, runtime_checkable

            @runtime_checkable
            class ProtocolDatabaseConfig(Protocol):
                host: str
                port: int
                username: str

            config = await reader.read_yaml('database.yaml', ProtocolDatabaseConfig)
            print(f"Database host: {config.host}")
            ```
        """
        ...

    async def exists(self, path: str) -> bool:
        """
        Check if a file exists at the specified path.

        Performs existence checking without requiring file access
        permissions, enabling safe file existence validation.

        Args:
            path: File path to check for existence

        Returns:
            True if file exists, False otherwise

        Example:
            ```python
            if await reader.exists('config.yaml'):
                config = await reader.read_yaml('config.yaml', Config)
            else:
                config = get_default_config()
            ```
        """
        ...
