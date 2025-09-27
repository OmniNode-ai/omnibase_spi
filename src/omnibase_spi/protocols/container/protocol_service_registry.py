"""
Service Registry Protocol - ONEX SPI Interface.

Comprehensive protocol definition for dependency injection service registration and management.
Supports the complete service lifecycle including registration, resolution, injection, and disposal.

Focuses purely on dependency injection patterns rather than artifact or service discovery concerns.
"""

from typing import Any, Literal, Protocol, Type, TypeVar, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralHealthStatus,
    LiteralOperationStatus,
    ProtocolDateTime,
    ProtocolSemVer,
)
from omnibase_spi.protocols.validation.protocol_validation import (
    ProtocolValidationResult,
)

T = TypeVar("T")
TInterface = TypeVar("TInterface")
TImplementation = TypeVar("TImplementation")
LiteralServiceLifecycle = Literal[
    "singleton", "transient", "scoped", "pooled", "lazy", "eager"
]
ServiceLifecycle = LiteralServiceLifecycle
LiteralServiceResolutionStatus = Literal[
    "resolved", "failed", "circular_dependency", "missing_dependency", "type_mismatch"
]
ServiceResolutionStatus = LiteralServiceResolutionStatus
LiteralInjectionScope = Literal[
    "request", "session", "thread", "process", "global", "custom"
]
InjectionScope = LiteralInjectionScope
ServiceHealthStatus = LiteralHealthStatus


@runtime_checkable
class ProtocolServiceRegistrationMetadata(Protocol):
    """Protocol for service registration metadata objects in service registry."""

    service_id: str
    service_name: str
    service_interface: str
    service_implementation: str
    version: "ProtocolSemVer"
    description: str | None
    tags: list[str]
    configuration: dict[str, "ContextValue"]
    created_at: "ProtocolDateTime"
    last_modified_at: "ProtocolDateTime | None"


@runtime_checkable
class ProtocolServiceDependency(Protocol):
    """Protocol for service dependency information."""

    dependency_name: str
    dependency_interface: str
    dependency_version: "ProtocolSemVer | None"
    is_required: bool
    is_circular: bool
    injection_point: str
    default_value: Any | None
    metadata: dict[str, "ContextValue"]

    def validate_dependency(self) -> bool:
        """Validate servicedependency data integrity and consistency."""
        ...

    def is_satisfied(self) -> bool:
        """Check if servicedependency satisfied."""
        ...


@runtime_checkable
class ProtocolServiceRegistration(Protocol):
    """Protocol for service registration information."""

    registration_id: str
    service_metadata: "ProtocolServiceRegistrationMetadata"
    lifecycle: LiteralServiceLifecycle
    scope: LiteralInjectionScope
    dependencies: list["ProtocolServiceDependency"]
    registration_status: Literal[
        "registered", "unregistered", "failed", "pending", "conflict", "invalid"
    ]
    health_status: ServiceHealthStatus
    registration_time: "ProtocolDateTime"
    last_access_time: "ProtocolDateTime | None"
    access_count: int
    instance_count: int
    max_instances: int | None

    def validate_registration(self) -> bool:
        """Validate serviceregistration data integrity and consistency."""
        ...

    def is_active(self) -> bool:
        """Check if serviceregistration active."""
        ...


@runtime_checkable
class ProtocolRegistryServiceInstance(Protocol):
    """Protocol for service registry managed instance information."""

    instance_id: str
    service_registration_id: str
    instance: Any
    lifecycle: LiteralServiceLifecycle
    scope: LiteralInjectionScope
    created_at: "ProtocolDateTime"
    last_accessed: "ProtocolDateTime"
    access_count: int
    is_disposed: bool
    metadata: dict[str, "ContextValue"]

    def validate_instance(self) -> bool:
        """Validate registryserviceinstance data integrity and consistency."""
        ...

    def is_active(self) -> bool:
        """Check if registryserviceinstance active."""
        ...


@runtime_checkable
class ProtocolDependencyGraph(Protocol):
    """Protocol for dependency graph information."""

    service_id: str
    dependencies: list[str]
    dependents: list[str]
    depth_level: int
    circular_references: list[str]
    resolution_order: list[str]
    metadata: dict[str, "ContextValue"]


@runtime_checkable
class ProtocolInjectionContext(Protocol):
    """Protocol for dependency injection context."""

    context_id: str
    target_service_id: str
    scope: LiteralInjectionScope
    resolved_dependencies: dict[str, Any]
    injection_time: "ProtocolDateTime"
    resolution_status: LiteralServiceResolutionStatus
    error_details: str | None
    resolution_path: list[str]
    metadata: dict[str, "ContextValue"]


@runtime_checkable
class ProtocolServiceRegistryStatus(Protocol):
    """Protocol for service registry status information."""

    registry_id: str
    status: LiteralOperationStatus
    message: str
    total_registrations: int
    active_instances: int
    failed_registrations: int
    circular_dependencies: int
    lifecycle_distribution: dict[LiteralServiceLifecycle, int]
    scope_distribution: dict[LiteralInjectionScope, int]
    health_summary: dict[ServiceHealthStatus, int]
    memory_usage_bytes: int | None
    average_resolution_time_ms: float | None
    last_updated: "ProtocolDateTime"


@runtime_checkable
class ProtocolServiceValidator(Protocol):
    """Protocol for service validation operations."""

    async def validate_service(
        self, service: Any, interface: Type[Any]
    ) -> ProtocolValidationResult:
        """Validate a service implementation against an interface."""
        ...

    async def validate_dependencies(
        self, dependencies: list["ProtocolServiceDependency"]
    ) -> ProtocolValidationResult:
        """Validate service dependencies."""
        ...


@runtime_checkable
class ProtocolServiceFactory(Protocol):
    """Protocol for service factory operations."""

    async def create_instance(self, interface: Type[T], context: dict[str, Any]) -> T:
        """Create a service instance."""
        ...

    async def dispose_instance(self, instance: Any) -> None:
        """Dispose of a service instance."""
        ...


@runtime_checkable
class ProtocolServiceRegistryConfig(Protocol):
    """Protocol for service registry configuration."""

    registry_name: str
    auto_wire_enabled: bool
    lazy_loading_enabled: bool
    circular_dependency_detection: bool
    max_resolution_depth: int
    instance_pooling_enabled: bool
    health_monitoring_enabled: bool
    performance_monitoring_enabled: bool
    configuration: dict[str, "ContextValue"]


@runtime_checkable
class ProtocolServiceRegistry(Protocol):
    """
    Protocol for service registry operations.

    Provides dependency injection service registration and management.
    Supports the complete service lifecycle including registration, resolution, injection, and disposal.

    Advanced Features:
        - **Lifecycle Management**: Support for singleton, transient, scoped, pooled patterns
        - **Dependency Injection**: Constructor, property, and method injection patterns
        - **Circular Dependency Detection**: Automatic detection and prevention
        - **Health Monitoring**: Service health tracking and validation
        - **Performance Metrics**: Resolution time tracking and optimization
        - **Scoped Injection**: Request, session, thread-based scoping
        - **Service Validation**: Registration and runtime validation
        - **Instance Pooling**: Object pooling for performance optimization

    Service Registration Patterns:
        - **Interface-based registration**: Register by interface type
        - **Named registration**: Register multiple implementations with names
        - **Generic registration**: Support for generic service types
        - **Conditional registration**: Register based on runtime conditions
        - **Decorator-based registration**: Use decorators for automatic registration
    """

    @property
    def config(self) -> ProtocolServiceRegistryConfig:
        """Get registry configuration protocol."""
        ...

    @property
    def validator(self) -> ProtocolServiceValidator | None:
        """Get service validator."""
        ...

    @property
    def factory(self) -> ProtocolServiceFactory | None:
        """Get service factory."""
        ...

    async def register_service(
        self,
        interface: Type[TInterface],
        implementation: Type[TImplementation],
        lifecycle: LiteralServiceLifecycle,
        scope: LiteralInjectionScope,
        configuration: dict[str, "ContextValue"] | None = None,
    ) -> str:
        """
        Register a service implementation for an interface.

        Args:
            interface: Service interface type
            implementation: Service implementation type
            lifecycle: Service lifecycle management
            scope: Dependency injection scope
            configuration: Optional service configuration

        Returns:
            Service registration ID

        Raises:
            ValueError: If registration is invalid or conflicts exist
        """
        ...

    async def register_instance(
        self,
        interface: Type[TInterface],
        instance: TInterface,
        scope: "LiteralInjectionScope" = "global",
        metadata: dict[str, "ContextValue"] | None = None,
    ) -> str:
        """
        Register a service instance directly.

        Args:
            interface: Service interface type
            instance: Service instance
            scope: Dependency injection scope
            metadata: Optional instance metadata

        Returns:
            Service registration ID
        """
        ...

    async def register_factory(
        self,
        interface: Type[TInterface],
        factory: "ProtocolServiceFactory",
        lifecycle: "LiteralServiceLifecycle" = "transient",
        scope: "LiteralInjectionScope" = "global",
    ) -> str:
        """
        Register a service factory for creating instances.

        Args:
            interface: Service interface type
            factory: Service factory
            lifecycle: Service lifecycle management
            scope: Dependency injection scope

        Returns:
            Service registration ID
        """
        ...

    async def unregister_service(self, registration_id: str) -> bool:
        """
        Unregister a service and dispose all instances.

        Args:
            registration_id: Service registration ID

        Returns:
            True if unregistration successful
        """
        ...

    async def resolve_service(
        self,
        interface: Type[TInterface],
        scope: "LiteralInjectionScope | None" = None,
        context: dict[str, "ContextValue"] | None = None,
    ) -> TInterface:
        """
        Resolve a service instance by interface.

        Args:
            interface: Service interface type
            scope: Optional scope override
            context: Optional resolution context

        Returns:
            Service instance

        Raises:
            ValueError: If service cannot be resolved
        """
        ...

    async def resolve_named_service(
        self,
        interface: Type[TInterface],
        name: str,
        scope: "LiteralInjectionScope | None" = None,
    ) -> TInterface:
        """
        Resolve a named service instance.

        Args:
            interface: Service interface type
            name: Service name
            scope: Optional scope override

        Returns:
            Named service instance
        """
        ...

    async def resolve_all_services(
        self, interface: Type[TInterface], scope: "LiteralInjectionScope | None" = None
    ) -> list[TInterface]:
        """
        Resolve all registered implementations of an interface.

        Args:
            interface: Service interface type
            scope: Optional scope override

        Returns:
            List of service instances
        """
        ...

    async def try_resolve_service(
        self, interface: Type[TInterface], scope: "LiteralInjectionScope | None" = None
    ) -> TInterface | None:
        """
        Try to resolve a service instance, return None if not found.

        Args:
            interface: Service interface type
            scope: Optional scope override

        Returns:
            Service instance or None if not found
        """
        ...

    async def get_registration(
        self, registration_id: str
    ) -> ProtocolServiceRegistration | None:
        """
        Get service registration by ID.

        Args:
            registration_id: Service registration ID

        Returns:
            Service registration or None if not found
        """
        ...

    async def get_registrations_by_interface(
        self, interface: Type[T]
    ) -> list["ProtocolServiceRegistration"]:
        """
        Get all registrations for an interface.

        Args:
            interface: Service interface type

        Returns:
            List of service registrations
        """
        ...

    async def get_all_registrations(self) -> list["ProtocolServiceRegistration"]:
        """
        Get all service registrations.

        Returns:
            List of all service registrations
        """
        ...

    async def get_active_instances(
        self, registration_id: str | None = None
    ) -> list["ProtocolRegistryServiceInstance"]:
        """
        Get active service instances.

        Args:
            registration_id: Optional filter by registration ID

        Returns:
            List of active service instances
        """
        ...

    async def dispose_instances(
        self, registration_id: str, scope: "LiteralInjectionScope | None" = None
    ) -> int:
        """
        Dispose service instances.

        Args:
            registration_id: Service registration ID
            scope: Optional scope filter

        Returns:
            Number of disposed instances
        """
        ...

    async def validate_registration(
        self, registration: "ProtocolServiceRegistration"
    ) -> bool:
        """
        Validate a service registration.

        Args:
            registration: Service registration to validate

        Returns:
            True if registration is valid
        """
        ...

    async def detect_circular_dependencies(
        self, registration: "ProtocolServiceRegistration"
    ) -> list[str]:
        """
        Detect circular dependencies for a registration.

        Args:
            registration: Service registration to check

        Returns:
            List of circular dependency paths
        """
        ...

    async def get_dependency_graph(
        self, service_id: str
    ) -> ProtocolDependencyGraph | None:
        """
        Get dependency graph for a service.

        Args:
            service_id: Service ID

        Returns:
            Dependency graph or None if service not found
        """
        ...

    async def get_registry_status(self) -> ProtocolServiceRegistryStatus:
        """
        Get comprehensive registry status.

        Returns:
            Registry status information
        """
        ...

    async def validate_service_health(
        self, registration_id: str
    ) -> ProtocolValidationResult:
        """
        Validate service health status.

        Args:
            registration_id: Service registration ID

        Returns:
            Validation result with health information
        """
        ...

    async def update_service_configuration(
        self, registration_id: str, configuration: dict[str, "ContextValue"]
    ) -> bool:
        """
        Update service configuration.

        Args:
            registration_id: Service registration ID
            configuration: New configuration values

        Returns:
            True if update successful
        """
        ...

    async def create_injection_scope(
        self, scope_name: str, parent_scope: str | None = None
    ) -> str:
        """
        Create a new injection scope.

        Args:
            scope_name: Name for the new scope
            parent_scope: Optional parent scope

        Returns:
            Created scope ID
        """
        ...

    async def dispose_injection_scope(self, scope_id: str) -> int:
        """
        Dispose an injection scope and all its instances.

        Args:
            scope_id: Scope ID to dispose

        Returns:
            Number of disposed instances
        """
        ...

    async def get_injection_context(
        self, context_id: str
    ) -> ProtocolInjectionContext | None:
        """
        Get injection context information.

        Args:
            context_id: Injection context ID

        Returns:
            Injection context or None if not found
        """
        ...
