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

    async def read_text(self, path: str) -> str: ...

    async def read_yaml(self, path: str, data_class: type[T]) -> T: ...

    async def exists(self, path: str) -> bool: ...
