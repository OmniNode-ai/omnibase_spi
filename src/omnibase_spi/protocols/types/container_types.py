"""
Container protocol types for ONEX SPI interfaces.

Domain: Dependency injection and service container protocols
"""

from typing import Literal, Protocol, runtime_checkable

from omnibase_spi.protocols.types.core_types import ContextValue, ProtocolSemVer

# Container status types
ContainerStatus = Literal["initializing", "ready", "error", "disposed"]

# Service lifecycle types
ServiceLifecycle = Literal["singleton", "transient", "scoped", "factory"]

# Dependency scope types
DependencyScope = Literal["required", "optional", "lazy", "eager"]


# Container protocols
@runtime_checkable
class ProtocolContainer(Protocol):
    """Protocol for dependency injection containers."""

    def register(self, service_key: str, service_instance: object) -> None:
        """Register service instance with container."""
        ...

    def get_service(self, service_key: str) -> object:
        """Retrieve service instance by key."""
        ...

    def has_service(self, service_key: str) -> bool:
        """Check if service is registered."""
        ...

    def dispose(self) -> None:
        """Dispose container and cleanup resources."""
        ...


class ProtocolDependencySpec(Protocol):
    """Protocol for dependency specification objects."""

    service_key: str
    module_path: str
    class_name: str
    lifecycle: ServiceLifecycle
    scope: DependencyScope
    configuration: dict[str, ContextValue]


class ProtocolServiceInstance(Protocol):
    """Protocol for service instance objects."""

    service_key: str
    instance_type: type
    lifecycle: ServiceLifecycle
    is_initialized: bool


class ProtocolRegistryWrapper(Protocol):
    """Protocol for registry wrapper objects."""

    def get_service(self, service_key: str) -> object:
        """Get service by key with fallback handling."""
        ...

    def get_node_version(self) -> ProtocolSemVer:
        """Get node version information."""
        ...

    def list_services(self) -> list[str]:
        """List all registered service keys."""
        ...


class ProtocolContainerResult(Protocol):
    """Protocol for container creation results."""

    container: ProtocolContainer
    registry: ProtocolRegistryWrapper
    status: ContainerStatus
    error_message: str | None
    services_registered: int


# Tool-related container protocols
class ProtocolToolClass(Protocol):
    """Protocol for tool class objects."""

    __name__: str
    __module__: str

    def __call__(self, *args: object, **kwargs: object) -> object:
        """Create tool instance."""
        ...


class ProtocolToolInstance(Protocol):
    """Protocol for tool instance objects."""

    tool_name: str
    tool_version: ProtocolSemVer
    is_initialized: bool

    def process(self, input_data: dict[str, ContextValue]) -> dict[str, ContextValue]:
        """Process input data and return results."""
        ...


# Container factory protocols
class ProtocolContainerFactory(Protocol):
    """Protocol for container factory objects."""

    def create_container(self) -> ProtocolContainer:
        """Create new container instance."""
        ...

    def create_registry_wrapper(
        self, container: ProtocolContainer
    ) -> ProtocolRegistryWrapper:
        """Create registry wrapper around container."""
        ...


class ProtocolServiceFactory(Protocol):
    """Protocol for service factory objects."""

    def create_service(
        self,
        dependency_spec: ProtocolDependencySpec,
    ) -> ProtocolServiceInstance:
        """Create service instance from dependency specification."""
        ...

    def validate_dependency(self, dependency_spec: ProtocolDependencySpec) -> bool:
        """Validate dependency specification."""
        ...


# Container configuration protocols
class ProtocolContainerConfiguration(Protocol):
    """Protocol for container configuration objects."""

    auto_registration: bool
    lazy_loading: bool
    validation_enabled: bool
    cache_services: bool
    configuration_overrides: dict[str, ContextValue]
