"""
Protocol for Service Discovery abstraction.

Provides a clean interface for service discovery systems (Consul, etcd, etc.)
with proper fallback strategies and error handling.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ProtocolServiceHealthStatus,
    ProtocolServiceInstance,
    ProtocolServiceMetadata,
)


@runtime_checkable
class ProtocolServiceDiscovery(Protocol):
    """
    Protocol for service discovery systems.

    Abstracts service registration, discovery, and health checking
    from specific implementations like Consul, etcd, or in-memory fallbacks.

    Key Features:
        - Service registration and deregistration
        - Service discovery with health filtering
        - Key-value store functionality
        - Health monitoring capabilities
        - Clean resource management
    """

    async def register_service(
        self,
        service_name: str,
        service_id: str,
        host: str,
        port: int,
        metadata: "ProtocolServiceMetadata",
        health_check_url: str | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        """
        Register a service with the discovery system.

        Args:
            service_name: Name of the service
            service_id: Unique identifier for this service instance
            host: Host where service is running
            port: Port where service is listening
            metadata: Service metadata as structured object
            health_check_url: Optional URL for health checks
            tags: Optional list of service tags

        Returns:
            True if registration successful, False otherwise

        Raises:
            ValueError: If service parameters are invalid
            RuntimeError: If discovery system is unavailable
        """
        ...

    async def deregister_service(self, service_id: str) -> bool:
        """
        Deregister a service from the discovery system.

        Args:
            service_id: Unique identifier of service to deregister

        Returns:
            True if deregistration successful, False otherwise

        Raises:
            ValueError: If service_id is invalid
            RuntimeError: If discovery system is unavailable
        """
        ...

    async def discover_services(
        self,
        service_name: str,
        healthy_only: bool = True,
        tags: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> tuple[list["ProtocolServiceInstance"], bool]:
        """
        Discover instances of a service with pagination support.

        Args:
            service_name: Name of service to discover
            healthy_only: If True, return only healthy instances
            tags: Optional list of tags to filter services
            limit: Optional maximum number of results to return
            offset: Optional offset for pagination

        Returns:
            Tuple of (service instances, has_more_results)

        Raises:
            ValueError: If service_name is invalid
            RuntimeError: If discovery system is unavailable

        Note:
            Pagination support prevents large result sets from impacting performance
            and enables incremental service discovery for large deployments.
        """
        ...

    async def get_service_health(
        self, service_id: str
    ) -> "ProtocolServiceHealthStatus":
        """
        Get health status of a specific service instance.

        Args:
            service_id: Unique identifier of service

        Returns:
            Service health information

        Raises:
            ValueError: If service_id is invalid or not found
            RuntimeError: If discovery system is unavailable
        """
        ...

    async def set_key_value(self, key: str, value: str) -> bool:
        """
        Set a key-value pair in the service discovery store.

        Args:
            key: Key to set
            value: Value to store

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If key or value format is invalid
            RuntimeError: If discovery system is unavailable
        """
        ...

    async def get_key_value(self, key: str) -> str | None:
        """
        Get value for a key from the service discovery store.

        Args:
            key: Key to retrieve

        Returns:
            Value if found, None if not found

        Raises:
            ValueError: If key format is invalid
            RuntimeError: If discovery system is unavailable
        """
        ...

    async def delete_key(self, key: str) -> bool:
        """
        Delete a key from the service discovery store.

        Args:
            key: Key to delete

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If key format is invalid
            RuntimeError: If discovery system is unavailable
        """
        ...

    async def list_keys(self, prefix: str) -> list[str]:
        """
        List keys with optional prefix filter.

        Args:
            prefix: Optional prefix to filter keys

        Returns:
            List of matching keys

        Raises:
            RuntimeError: If discovery system is unavailable
        """
        ...

    async def health_check(self) -> bool:
        """
        Check if the service discovery system is healthy.

        Returns:
            True if healthy, False otherwise
        """
        ...

    async def close(self) -> None:
        """
        Clean up resources and close connections.

        Should be called when the service discovery client is no longer needed.
        """
        ...
