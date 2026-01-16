"""
Generic Container Protocol - ONEX SPI Interface.

Provides a protocol interface for generic value containers with metadata support.
This protocol enables type-safe value wrapping with arbitrary metadata attachment
without forcing dependency on concrete container implementations.

Key Features:
    - Generic type support for any wrapped value type
    - Metadata dictionary for extensible container attributes
    - Type-safe access to wrapped values and metadata
    - Framework-agnostic container abstraction
"""

from typing import TYPE_CHECKING, Generic, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType

T = TypeVar("T", covariant=True)


@runtime_checkable
class ProtocolContainer(Protocol, Generic[T]):
    """
    Protocol for generic value containers with metadata.

    Defines the interface for containers that wrap values with associated metadata.
    This protocol enables implementations to provide consistent container behavior
    across different subsystems while maintaining type safety through generics.

    Type Parameters:
        T: The type of the wrapped value

    Attributes:
        value: The wrapped value of type T
        metadata: Dictionary containing arbitrary metadata associated with the container

    Methods:
        get_metadata: Retrieve specific metadata value with optional default

    Example:
        ```python
        from omnibase_spi.protocols.container import ProtocolContainer

        # Get container implementation (from service registry, factory, etc.)
        container: ProtocolContainer[str] = get_container(
            value="example_data",
            metadata={"source": "api", "timestamp": "2025-01-15T10:30:00Z"}
        )

        # Type-safe value access
        data: str = container.value  # Type checker knows this is str
        source: str = container.get_metadata("source", "unknown")

        # Access all metadata
        all_meta: dict = container.metadata
        print(f"Source: {all_meta['source']}, Timestamp: {all_meta['timestamp']}")
        ```

    Use Cases:
        - Service resolution results with metadata (lifecycle, scope, etc.)
        - Event payloads with routing and tracing information
        - Configuration values with source and validation metadata
        - API responses with headers and status information
        - Tool execution results with performance metrics
    """

    @property
    def value(self) -> T:
        """
        Get the wrapped value.

        Returns:
            The value of type T stored in this container

        Example:
            ```python
            container: ProtocolContainer[int] = create_container(42)
            number: int = container.value  # Returns 42
            ```
        """
        ...

    @property
    def metadata(self) -> "JsonType":
        """
        Get container metadata.

        Returns:
            Dictionary containing all metadata associated with this container.
            Implementations should return a copy to prevent external mutation.

        Example:
            ```python
            container: ProtocolContainer[str] = create_container(
                value="data",
                metadata={"source": "cache", "ttl": 300}
            )
            all_metadata: dict = container.metadata
            # Returns: {"source": "cache", "ttl": 300}
            ```
        """
        ...

    def get_metadata(self, key: str, default: "JsonType | None" = None) -> "JsonType":
        """
        Get specific metadata field.

        Provides convenient access to individual metadata values with default
        fallback support.

        Args:
            key: The metadata key to retrieve
            default: Value to return if key is not found (defaults to None)

        Returns:
            The metadata value for the specified key, or default if not found

        Example:
            ```python
            container: ProtocolContainer[str] = create_container(
                value="data",
                metadata={"source": "api", "retries": 3}
            )

            source: str = container.get_metadata("source", "unknown")  # Returns "api"
            timeout: int = container.get_metadata("timeout", 30)  # Returns 30 (default)
            retries: int = container.get_metadata("retries")  # Returns 3
            ```
        """
        ...
