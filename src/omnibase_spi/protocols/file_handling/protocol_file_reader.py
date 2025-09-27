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
    Protocol for reading file contents.

    This abstraction allows for different implementations:
    - FileSystemFileReader: Reads from actual filesystem
    - MockFileReader: Returns predefined content for testing
    - RemoteFileReader: Could read from S3, HTTP, etc.
    """

    async def read_text(self, path: str) -> str:
        """
        Read text content from a file.

        Args:
            path: Path to the file to read

        Returns:
            str: The text content of the file

        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        ...

    async def read_yaml(self, path: str, data_class: type[T]) -> T:
        """
        Read and parse YAML content from a file into a Pydantic data.

        Args:
            path: Path to the YAML file to read
            data_class: Pydantic data class to validate and parse into

        Returns:
            Instance of the specified Pydantic data

        Raises:
            OnexError: If the file doesn't exist (FILE_NOT_FOUND)
            OnexError: If there's an error reading the file (FILE_READ_ERROR)
            OnexError: If the YAML is malformed (YAML_PARSE_ERROR)
            OnexError: If the YAML doesn't match the data schema (VALIDATION_ERROR)
        """
        ...

    async def exists(self, path: str) -> bool:
        """
        Check if a file exists.

        Args:
            path: Path to check

        Returns:
            bool: True if the file exists, False otherwise
        """
        ...
