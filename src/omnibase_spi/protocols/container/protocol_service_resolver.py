"""
Service Resolver Protocol - ONEX SPI Interface.

Protocol for service resolution operations including protocol-based lookup,
name-based resolution, and service instance management in dependency injection
containers.
"""

from typing import Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class ProtocolServiceResolver(Protocol):
    """
    Protocol for service resolution operations.

    Provides service lookup and resolution capabilities for dependency
    injection containers, supporting both protocol-based and name-based
    service resolution patterns. This protocol enables flexible service
    resolution across different container implementations while maintaining
    type safety and consistent interfaces.

    The resolver supports multiple resolution strategies:
    - Protocol type resolution: Resolve by protocol interface type
    - Name-based resolution: Resolve by service name string
    - Hybrid resolution: Resolve using both protocol type and specific name

    Key Features:
        - Type-safe protocol-based resolution
        - String-based service name resolution
        - Support for multiple service implementations
        - Consistent error handling for missing services
        - Integration with service registry patterns
        - Flexible resolution strategies

    Example:
        ```python
        resolver: ProtocolServiceResolver = create_service_resolver()

        # Protocol type resolution
        event_bus = resolver.get_service(ProtocolEventBus)

        # Name-based resolution
        cache_service = resolver.get_service("cache_service")

        # Hybrid resolution (protocol type + specific name)
        user_repo = resolver.get_service(ProtocolRepository, "user_repository")
        ```

    Resolution Workflow:
        1. Check if protocol_type_or_name is a string
        2. If string, resolve by service name
        3. If type, extract protocol name and resolve by protocol
        4. Support optional service_name for disambiguation
        5. Return service instance or raise resolution error

    Error Handling:
        The resolver should raise appropriate errors when:
        - Service name not registered
        - Protocol type not implemented by any service
        - Multiple services match without disambiguation
        - Service instance creation fails

    See Also:
        - ProtocolServiceRegistry: Service registration and management
        - ProtocolDIServiceInstance: Service instance metadata
        - ProtocolConfigurationManager: Service configuration
    """

    async def get_service(
        self,
        protocol_type_or_name: type[T] | str,
        service_name: str | None = None,
    ) -> object:
        """
        Get service instance for protocol type or service name.

        Resolves and returns a service instance based on either a protocol
        type interface or a service name string. Supports optional service_name
        parameter for disambiguating multiple implementations of the same protocol.

        Args:
            protocol_type_or_name: Protocol type (e.g., ProtocolEventBus) or
                service name string (e.g., "event_bus", "cache_service")
            service_name: Optional specific service name for disambiguation when
                multiple implementations exist for the same protocol type

        Returns:
            Service instance implementing the protocol or matching the service name.
            The return type depends on the protocol type or service configuration.

        Raises:
            Exception: If service cannot be resolved due to:
                - Service name not registered
                - Protocol type not implemented
                - Multiple services without disambiguation
                - Service creation failure
                (Specific exception type depends on implementation)

        Example:
            ```python
            # Protocol type resolution
            event_bus = resolver.get_service(ProtocolEventBus)

            # String name resolution
            cache = resolver.get_service("cache_service")

            # Hybrid resolution (protocol + name)
            user_repo = resolver.get_service(ProtocolRepository, "user_repository")
            admin_repo = resolver.get_service(ProtocolRepository, "admin_repository")
            ```

        Resolution Priority:
            1. If protocol_type_or_name is string and service_name is None:
               Resolve by service name string
            2. If protocol_type_or_name is type:
               Resolve by protocol interface type
            3. If both protocol_type and service_name provided:
               Resolve by protocol type with specific name filter

        Thread Safety:
            Resolution behavior depends on implementation. Implementations should
            document thread safety guarantees for concurrent service resolution.
        """
        ...
