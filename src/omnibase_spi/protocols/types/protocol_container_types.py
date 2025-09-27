"""
Container protocol types for ONEX SPI interfaces.

Domain: Dependency injection and service container protocols
"""

from typing import Literal, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    ProtocolSemVer,
)

# Container status types
LiteralContainerStatus = Literal["initializing", "ready", "error", "disposed"]

# Service lifecycle types
LiteralServiceLifecycle = Literal["singleton", "transient", "scoped", "factory"]

# Dependency scope types
LiteralDependencyScope = Literal["required", "optional", "lazy", "eager"]


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


@runtime_checkable
class ProtocolDependencySpec(Protocol):
    """Protocol for dependency specification objects."""

    service_key: str
    module_path: str
    class_name: str
    lifecycle: LiteralServiceLifecycle
    scope: LiteralDependencyScope
    configuration: dict[str, "ContextValue"]


@runtime_checkable
class ProtocolContainerServiceInstance(Protocol):
    """Protocol for dependency injection container service instance objects."""

    service_key: str
    instance_type: type
    lifecycle: LiteralServiceLifecycle
    is_initialized: bool

    def validate_service_instance(self) -> bool:
        """Validate containerserviceinstance data integrity and consistency."""
        ...

    async def is_ready_for_use(self) -> bool:
        """Check if containerserviceinstance ready for use."""
        ...


@runtime_checkable
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


@runtime_checkable
class ProtocolContainerResult(Protocol):
    """Protocol for container creation results."""

    container: "ProtocolContainer"
    registry: "ProtocolRegistryWrapper"
    status: LiteralContainerStatus
    error_message: str | None
    services_registered: int


# Note: "ProtocolToolClass" is defined in protocol_mcp_types.py
# Tool instances in container context
@runtime_checkable
class ProtocolContainerToolInstance(Protocol):
    """Protocol for tool instance objects in dependency injection container context."""

    tool_name: str
    tool_version: "ProtocolSemVer"
    is_initialized: bool

    async def process(
        self, input_data: dict[str, "ContextValue"]
    ) -> dict[str, "ContextValue"]:
        """Process input data and return results."""
        ...


# Container factory protocols
@runtime_checkable
class ProtocolContainerFactory(Protocol):
    """Protocol for container factory objects."""

    def create_container(self) -> ProtocolContainer:
        """Create new container instance."""
        ...

    def create_registry_wrapper(
        self, container: "ProtocolContainer"
    ) -> ProtocolRegistryWrapper:
        """Create registry wrapper around container."""
        ...


@runtime_checkable
class ProtocolContainerServiceFactory(Protocol):
    """Protocol for dependency injection container service factory objects."""

    def create_service(
        self,
        dependency_spec: "ProtocolDependencySpec",
    ) -> ProtocolContainerServiceInstance:
        """Create service instance from dependency specification."""
        ...

    def validate_dependency(self, dependency_spec: "ProtocolDependencySpec") -> bool:
        """Validate dependency specification."""
        ...


# Container configuration protocols
@runtime_checkable
class ProtocolContainerConfiguration(Protocol):
    """Protocol for container configuration objects."""

    auto_registration: bool
    lazy_loading: bool
    validation_enabled: bool
    cache_services: bool
    configuration_overrides: dict[str, "ContextValue"]
