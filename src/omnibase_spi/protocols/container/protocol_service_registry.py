"""
Service Registry Protocol - ONEX SPI Interface.

Comprehensive protocol definition for dependency injection service registration and management.
Supports the complete service lifecycle including registration, resolution, injection, and disposal.

Focuses purely on dependency injection patterns rather than artifact or service discovery concerns.
"""

from typing import TYPE_CHECKING, Any, Literal, Protocol, Type, TypeVar, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralHealthStatus,
    LiteralOperationStatus,
    ProtocolDateTime,
    ProtocolSemVer,
)

if TYPE_CHECKING:
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

    async def validate_dependency(self) -> bool: ...

    def is_satisfied(self) -> bool: ...


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

    async def validate_registration(self) -> bool: ...

    def is_active(self) -> bool: ...


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

    async def validate_instance(self) -> bool: ...

    def is_active(self) -> bool: ...


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
    resolved_dependencies: dict[str, "ContextValue"]
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
    ) -> "ProtocolValidationResult": ...

    async def validate_dependencies(
        self, dependencies: list["ProtocolServiceDependency"]
    ) -> "ProtocolValidationResult": ...


@runtime_checkable
class ProtocolServiceFactory(Protocol):
    """Protocol for service factory operations."""

    async def create_instance(
        self, interface: Type[T], context: dict[str, "ContextValue"]
    ) -> T: ...

    async def dispose_instance(self, instance: Any) -> None: ...


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
    def config(self) -> ProtocolServiceRegistryConfig: ...

    @property
    def validator(self) -> ProtocolServiceValidator | None: ...

    @property
    def factory(self) -> ProtocolServiceFactory | None: ...

    async def register_service(
        self,
        interface: Type[TInterface],
        implementation: Type[TImplementation],
        lifecycle: LiteralServiceLifecycle,
        scope: LiteralInjectionScope,
        configuration: dict[str, "ContextValue"] | None = None,
    ) -> str: ...

    async def register_instance(
        self,
        interface: Type[TInterface],
        instance: TInterface,
        scope: "LiteralInjectionScope" = "global",
        metadata: dict[str, "ContextValue"] | None = None,
    ) -> str: ...

    async def register_factory(
        self,
        interface: Type[TInterface],
        factory: "ProtocolServiceFactory",
        lifecycle: "LiteralServiceLifecycle" = "transient",
        scope: "LiteralInjectionScope" = "global",
    ) -> str: ...

    async def unregister_service(self, registration_id: str) -> bool: ...

    async def resolve_service(
        self,
        interface: Type[TInterface],
        scope: "LiteralInjectionScope | None" = None,
        context: dict[str, "ContextValue"] | None = None,
    ) -> TInterface: ...

    async def resolve_named_service(
        self,
        interface: Type[TInterface],
        name: str,
        scope: "LiteralInjectionScope | None" = None,
    ) -> TInterface: ...

    async def resolve_all_services(
        self, interface: Type[TInterface], scope: "LiteralInjectionScope | None" = None
    ) -> list[TInterface]: ...

    async def try_resolve_service(
        self, interface: Type[TInterface], scope: "LiteralInjectionScope | None" = None
    ) -> TInterface | None: ...

    async def get_registration(
        self, registration_id: str
    ) -> ProtocolServiceRegistration | None: ...

    async def get_registrations_by_interface(
        self, interface: Type[T]
    ) -> list["ProtocolServiceRegistration"]: ...

    async def get_all_registrations(self) -> list["ProtocolServiceRegistration"]: ...

    async def get_active_instances(
        self, registration_id: str | None = None
    ) -> list["ProtocolRegistryServiceInstance"]: ...

    async def dispose_instances(
        self, registration_id: str, scope: "LiteralInjectionScope | None" = None
    ) -> int: ...

    async def validate_registration(
        self, registration: "ProtocolServiceRegistration"
    ) -> bool: ...

    async def detect_circular_dependencies(
        self, registration: "ProtocolServiceRegistration"
    ) -> list[str]: ...

    async def get_dependency_graph(
        self, service_id: str
    ) -> ProtocolDependencyGraph | None: ...

    async def get_registry_status(self) -> ProtocolServiceRegistryStatus: ...

    async def validate_service_health(
        self, registration_id: str
    ) -> "ProtocolValidationResult": ...

    async def update_service_configuration(
        self, registration_id: str, configuration: dict[str, "ContextValue"]
    ) -> bool: ...

    async def create_injection_scope(
        self, scope_name: str, parent_scope: str | None = None
    ) -> str: ...

    async def dispose_injection_scope(self, scope_id: str) -> int: ...

    async def get_injection_context(
        self, context_id: str
    ) -> ProtocolInjectionContext | None: ...
