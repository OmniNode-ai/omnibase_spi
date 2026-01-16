"""
Container protocol types for ONEX SPI interfaces.

Domain: Dependency injection and service container protocols
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ContextValue,
        ProtocolSemVer,
    )

LiteralContainerStatus = Literal["initializing", "ready", "error", "disposed"]
LiteralServiceLifecycle = Literal["singleton", "transient", "scoped", "factory"]
LiteralDependencyScope = Literal["required", "optional", "lazy", "eager"]


@runtime_checkable
class ProtocolDIContainer(Protocol):
    """
    Protocol for dependency injection containers managing service lifecycle.

    Provides service registration, resolution, and lifecycle management
    for dependency injection. Supports registration of factory functions
    and retrieval of service instances.

    Note: Renamed from ProtocolContainer to avoid conflict with
    ProtocolContainer in container/protocol_container.py which is for
    generic value containers with metadata.

    Attributes:
        register: Method to register a service factory.
        get_service: Async method to resolve a service by key.
        has_service: Method to check service availability.
        dispose: Method to clean up container resources.

    Example:
        ```python
        class SimpleDIContainer:
            _services: dict = {}

            def register(
                self, service_key: str, service_instance: Callable[..., object]
            ) -> None:
                self._services[service_key] = service_instance

            async def get_service(self, service_key: str) -> object:
                return self._services[service_key]()

            def has_service(self, service_key: str) -> bool:
                return service_key in self._services

            def dispose(self) -> None:
                self._services.clear()

        container = SimpleDIContainer()
        assert isinstance(container, ProtocolDIContainer)
        ```
    """

    def register(
        self, service_key: str, service_instance: Callable[..., object]
    ) -> None: ...

    async def get_service(self, service_key: str) -> object: ...

    def has_service(self, service_key: str) -> bool: ...

    def dispose(self) -> None: ...


@runtime_checkable
class ProtocolDependencySpec(Protocol):
    """
    Protocol for dependency specification and configuration.

    Defines how a service should be instantiated and managed including
    module location, lifecycle behavior, and configuration parameters.
    Used for declarative service registration.

    Attributes:
        service_key: Unique key for service identification.
        module_path: Python module path containing the service class.
        class_name: Name of the service class within the module.
        lifecycle: Service instance lifecycle (singleton, transient, etc.).
        scope: Dependency resolution scope (required, optional, etc.).
        configuration: Service-specific configuration parameters.

    Example:
        ```python
        class CacheServiceSpec:
            service_key: str = "cache_service"
            module_path: str = "app.services.cache"
            class_name: str = "RedisCacheService"
            lifecycle: LiteralServiceLifecycle = "singleton"
            scope: LiteralDependencyScope = "required"
            configuration: dict[str, ContextValue] = {
                "host": "localhost",
                "port": 6379,
                "db": 0
            }

        spec = CacheServiceSpec()
        assert isinstance(spec, ProtocolDependencySpec)
        ```
    """

    service_key: str
    module_path: str
    class_name: str
    lifecycle: LiteralServiceLifecycle
    scope: LiteralDependencyScope
    configuration: dict[str, "ContextValue"]


@runtime_checkable
class ProtocolContainerServiceInstance(Protocol):
    """
    Protocol for managed service instances within DI containers.

    Represents an instantiated service with its type information,
    lifecycle classification, and initialization state. Used for
    service instance tracking and management.

    Attributes:
        service_key: Key used to register/retrieve the service.
        instance_type: The Python type of the service instance.
        lifecycle: How the instance lifecycle is managed.
        is_initialized: Whether the instance has been fully initialized.

    Example:
        ```python
        class ManagedCacheInstance:
            service_key: str = "cache_service"
            instance_type: type = RedisCacheService
            lifecycle: LiteralServiceLifecycle = "singleton"
            is_initialized: bool = True

            async def validate_service_instance(self) -> bool:
                return self.is_initialized

        instance = ManagedCacheInstance()
        assert isinstance(instance, ProtocolContainerServiceInstance)
        ```
    """

    service_key: str
    instance_type: type
    lifecycle: LiteralServiceLifecycle
    is_initialized: bool

    async def validate_service_instance(self) -> bool: ...


@runtime_checkable
class ProtocolRegistryWrapper(Protocol):
    """
    Protocol for registry wrapper providing service access and versioning.

    Wraps a service registry to provide simplified service access and
    version information. Used as a facade for container operations.

    Attributes:
        get_service: Async method to resolve a service by key.
        get_node_version: Async method to get registry version.

    Example:
        ```python
        class RegistryWrapperImpl:
            _container: ProtocolDIContainer = container_impl
            _version: ProtocolSemVer = semver_impl

            async def get_service(self, service_key: str) -> object:
                return await self._container.get_service(service_key)

            async def get_node_version(self) -> ProtocolSemVer:
                return self._version

        wrapper = RegistryWrapperImpl()
        assert isinstance(wrapper, ProtocolRegistryWrapper)
        ```
    """

    async def get_service(self, service_key: str) -> object: ...

    async def get_node_version(self) -> "ProtocolSemVer": ...


@runtime_checkable
class ProtocolContainerResult(Protocol):
    """
    Protocol for container initialization and creation results.

    Contains the outcome of container creation including the container
    instance, registry wrapper, status, and registration statistics.
    Used for container factory return values.

    Attributes:
        container: The created DI container instance.
        registry: Registry wrapper for service access.
        status: Current container status.
        error_message: Error details if initialization failed.
        services_registered: Count of successfully registered services.

    Example:
        ```python
        class ContainerCreationResult:
            container: ProtocolDIContainer = container_impl
            registry: ProtocolRegistryWrapper = registry_impl
            status: LiteralContainerStatus = "ready"
            error_message: str | None = None
            services_registered: int = 15

        result = ContainerCreationResult()
        assert isinstance(result, ProtocolContainerResult)
        ```
    """

    container: "ProtocolDIContainer"
    registry: "ProtocolRegistryWrapper"
    status: LiteralContainerStatus
    error_message: str | None
    services_registered: int


@runtime_checkable
class ProtocolContainerToolInstance(Protocol):
    """
    Protocol for tool instances managed within a DI container context.

    Represents a processing tool with version tracking and initialization
    state. Provides a process method for input/output transformation.
    Used for container-managed tool execution.

    Attributes:
        tool_name: Identifier name of the tool.
        tool_version: Semantic version of the tool.
        is_initialized: Whether the tool is ready for use.
        process: Async method to process input data.

    Example:
        ```python
        class JsonValidatorTool:
            tool_name: str = "json_validator"
            tool_version: ProtocolSemVer = semver_impl
            is_initialized: bool = True

            async def process(
                self, input_data: dict[str, ContextValue]
            ) -> dict[str, ContextValue]:
                # Validate and return result
                return {"valid": True, "errors": []}

        tool = JsonValidatorTool()
        assert isinstance(tool, ProtocolContainerToolInstance)
        ```
    """

    tool_name: str
    tool_version: "ProtocolSemVer"
    is_initialized: bool

    async def process(
        self, input_data: dict[str, "ContextValue"]
    ) -> dict[str, "ContextValue"]: ...


@runtime_checkable
class ProtocolContainerFactory(Protocol):
    """
    Protocol for factory creating DI containers and registry wrappers.

    Provides factory methods for creating configured container instances
    and their associated registry wrappers. Used for container bootstrapping.

    Attributes:
        create_container: Async method to create a new container.
        create_registry_wrapper: Async method to wrap a container.

    Example:
        ```python
        class StandardContainerFactory:
            async def create_container(self) -> ProtocolDIContainer:
                container = SimpleDIContainer()
                # Register default services
                return container

            async def create_registry_wrapper(
                self, container: ProtocolDIContainer
            ) -> ProtocolRegistryWrapper:
                return RegistryWrapperImpl(container)

        factory = StandardContainerFactory()
        assert isinstance(factory, ProtocolContainerFactory)
        container = await factory.create_container()
        ```
    """

    async def create_container(self) -> ProtocolDIContainer: ...

    async def create_registry_wrapper(
        self, container: "ProtocolDIContainer"
    ) -> ProtocolRegistryWrapper: ...


@runtime_checkable
class ProtocolContainerServiceFactory(Protocol):
    """
    Protocol for factory creating service instances from specifications.

    Creates service instances based on dependency specifications and
    validates specifications before instantiation. Used for dynamic
    service creation within containers.

    Attributes:
        create_service: Async method to instantiate from spec.
        validate_dependency: Async method to validate spec before creation.

    Example:
        ```python
        class DynamicServiceFactory:
            async def create_service(
                self, dependency_spec: ProtocolDependencySpec
            ) -> ProtocolContainerServiceInstance:
                module = importlib.import_module(dependency_spec.module_path)
                cls = getattr(module, dependency_spec.class_name)
                instance = cls(**dependency_spec.configuration)
                return ServiceInstanceImpl(
                    service_key=dependency_spec.service_key,
                    instance_type=cls,
                    lifecycle=dependency_spec.lifecycle,
                    is_initialized=True
                )

            async def validate_dependency(
                self, dependency_spec: ProtocolDependencySpec
            ) -> bool:
                return bool(dependency_spec.service_key)

        factory = DynamicServiceFactory()
        assert isinstance(factory, ProtocolContainerServiceFactory)
        ```
    """

    async def create_service(
        self, dependency_spec: "ProtocolDependencySpec"
    ) -> ProtocolContainerServiceInstance: ...

    async def validate_dependency(
        self, dependency_spec: "ProtocolDependencySpec"
    ) -> bool: ...


@runtime_checkable
class ProtocolContainerConfiguration(Protocol):
    """
    Protocol for DI container configuration and behavior settings.

    Defines container behavior including auto-registration, lazy loading,
    validation, and caching preferences. Used for container initialization.

    Attributes:
        auto_registration: Whether to auto-discover and register services.
        lazy_loading: Whether to defer service creation until first use.
        validation_enabled: Whether to validate dependencies at startup.
        cache_services: Whether to cache singleton instances.
        configuration_overrides: Service configuration overrides.

    Example:
        ```python
        class ProductionContainerConfig:
            auto_registration: bool = True
            lazy_loading: bool = True
            validation_enabled: bool = True
            cache_services: bool = True
            configuration_overrides: dict[str, ContextValue] = {
                "database.pool_size": 20,
                "cache.ttl_seconds": 3600
            }

        config = ProductionContainerConfig()
        assert isinstance(config, ProtocolContainerConfiguration)
        ```
    """

    auto_registration: bool
    lazy_loading: bool
    validation_enabled: bool
    cache_services: bool
    configuration_overrides: dict[str, "ContextValue"]
