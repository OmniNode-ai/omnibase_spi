"""
Container protocol types for ONEX SPI interfaces.

Domain: Dependency injection and service container protocols
"""

from typing import Any, Callable, Literal, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    ProtocolSemVer,
)

LiteralContainerStatus = Literal["initializing", "ready", "error", "disposed"]
LiteralServiceLifecycle = Literal["singleton", "transient", "scoped", "factory"]
LiteralDependencyScope = Literal["required", "optional", "lazy", "eager"]


@runtime_checkable
class ProtocolContainer(Protocol):
    """Protocol for dependency injection containers."""

    def register(
        self, service_key: str, service_instance: Callable[..., Any]
    ) -> None: ...

    async def get_service(self, service_key: str) -> object: ...

    def has_service(self, service_key: str) -> bool: ...

    def dispose(self) -> None: ...


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

    async def validate_service_instance(self) -> bool: ...


@runtime_checkable
class ProtocolRegistryWrapper(Protocol):
    """Protocol for registry wrapper objects."""

    async def get_service(self, service_key: str) -> object: ...

    async def get_node_version(self) -> ProtocolSemVer: ...


@runtime_checkable
class ProtocolContainerResult(Protocol):
    """Protocol for container creation results."""

    container: "ProtocolContainer"
    registry: "ProtocolRegistryWrapper"
    status: LiteralContainerStatus
    error_message: str | None
    services_registered: int


@runtime_checkable
class ProtocolContainerToolInstance(Protocol):
    """Protocol for tool instance objects in dependency injection container context."""

    tool_name: str
    tool_version: "ProtocolSemVer"
    is_initialized: bool

    async def process(
        self, input_data: dict[str, "ContextValue"]
    ) -> dict[str, "ContextValue"]: ...


@runtime_checkable
class ProtocolContainerFactory(Protocol):
    """Protocol for container factory objects."""

    async def create_container(self) -> ProtocolContainer: ...

    async def create_registry_wrapper(
        self, container: "ProtocolContainer"
    ) -> ProtocolRegistryWrapper: ...


@runtime_checkable
class ProtocolContainerServiceFactory(Protocol):
    """Protocol for dependency injection container service factory objects."""

    async def create_service(
        self, dependency_spec: "ProtocolDependencySpec"
    ) -> ProtocolContainerServiceInstance: ...

    async def validate_dependency(
        self, dependency_spec: "ProtocolDependencySpec"
    ) -> bool: ...


@runtime_checkable
class ProtocolContainerConfiguration(Protocol):
    """Protocol for container configuration objects."""

    auto_registration: bool
    lazy_loading: bool
    validation_enabled: bool
    cache_services: bool
    configuration_overrides: dict[str, "ContextValue"]
