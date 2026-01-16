"""
Service Registry Protocol - ONEX SPI Interface.

Comprehensive protocol definition for dependency injection service registration and management.
Supports the complete service lifecycle including registration, resolution, injection, and disposal.

Focuses purely on dependency injection patterns rather than artifact or service discovery concerns.
"""

from typing import (
    TYPE_CHECKING,
    Literal,
    Protocol,
    TypeVar,
    runtime_checkable,
)

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ContextValue,
        ProtocolDateTime,
        ProtocolSemVer,
    )
    from omnibase_spi.protocols.validation.protocol_validation import (
        ProtocolValidationResult,
    )

from omnibase_spi.protocols.types.protocol_core_types import (
    LiteralHealthStatus,
    LiteralOperationStatus,
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
    """
    Protocol for service dependency information.

    Defines the interface for service dependency metadata including version constraints,
    circular dependency detection, injection points, and validation capabilities. This
    protocol enables comprehensive dependency management and resolution across the
    ONEX ecosystem.

    Attributes:
        dependency_name: Unique identifier for the dependency
        dependency_interface: Interface type that the dependency provides
        dependency_version: Version constraint for the dependency (optional)
        is_required: Whether this dependency is required or optional
        is_circular: Whether this dependency creates a circular reference
        injection_point: Location where dependency should be injected
        default_value: Default value if dependency cannot be resolved (optional)
        metadata: Additional dependency configuration and metadata

    Methods:
        validate_dependency: Validate that dependency constraints are satisfied
        is_satisfied: Check if dependency requirements are currently met

    Example:
        ```python
        @runtime_checkable
        class ServiceDependencyImpl:
            dependency_name: str | None = None
            dependency_interface: str | None = None
            dependency_version: "ProtocolSemVer | None = "1.0.0"
            is_required: bool | None = None
            is_circular: bool | None = None
            injection_point: str | None = None
            default_value: object | None = None
            metadata: dict[str, "ContextValue"] = {"timeout": 30}

            async def validate_dependency(self) -> bool:
                # Validate version compatibility and interface implementation
                return await check_version_compatibility(self.dependency_version)

            def is_satisfied(self) -> bool:
                # Check if dependency is currently available
                return service_container.has_service(self.dependency_interface)

        # Usage in service registration
        dependency: ProtocolServiceDependency = ServiceDependencyImpl()
        if await dependency.validate_dependency():
            register_dependency(dependency)
        ```

    Dependency Resolution:
        The protocol supports complex dependency scenarios including version constraints,
        optional dependencies, circular reference detection, and injection point specification
        for robust dependency management.
    """

    dependency_name: str
    dependency_interface: str
    dependency_version: "ProtocolSemVer | None"
    is_required: bool
    is_circular: bool
    injection_point: str
    default_value: "ContextValue | None"
    metadata: dict[str, "ContextValue"]

    async def validate_dependency(self) -> bool: ...

    def is_satisfied(self) -> bool: ...


@runtime_checkable
class ProtocolServiceRegistration(Protocol):
    """
    Protocol for service registration information.

    Defines the interface for comprehensive service registration metadata including
    lifecycle management, dependency tracking, health monitoring, and usage statistics.
    This protocol enables robust service lifecycle management across the ONEX ecosystem.

    Attributes:
        registration_id: Unique identifier for this registration
        service_metadata: Comprehensive metadata about the service
        lifecycle: Lifecycle pattern (singleton, transient, scoped, etc.)
        scope: Injection scope for instance management
        dependencies: List of service dependencies for this registration
        registration_status: Current status of the registration
        health_status: Health monitoring status for the service
        registration_time: When this registration was created
        last_access_time: When this service was last accessed
        access_count: Number of times this service has been accessed
        instance_count: Number of active instances (for non-singleton lifecycles)
        max_instances: Maximum allowed instances (for pooled lifecycles)

    Methods:
        validate_registration: Validate that registration is valid and complete
        is_active: Check if this registration is currently active

    Example:
        ```python
        @runtime_checkable
        class ServiceRegistrationImpl:
            registration_id: str | None = None
            service_metadata: ProtocolServiceRegistrationMetadata = metadata
            lifecycle: LiteralServiceLifecycle = "singleton"
            scope: LiteralInjectionScope = "global"
            dependencies: list[ProtocolServiceDependency] = []
            registration_status: str | None = None
            health_status: ServiceHealthStatus = "healthy"
            registration_time: "ProtocolDateTime" = current_time()
            last_access_time: "ProtocolDateTime" | None = None
            access_count: int | None = None
            instance_count: int | None = None
            max_instances: int | None = None

            async def validate_registration(self) -> bool:
                # Validate metadata, dependencies, and lifecycle constraints
                return (await self._validate_dependencies() and
                       await self._validate_lifecycle_constraints())

            def is_active(self) -> bool:
                return (self.registration_status == "registered" and
                       self.health_status == "healthy")

        # Usage in service registry operations
        registration: ProtocolServiceRegistration = ServiceRegistrationImpl()
        if registration.is_active():
            service = await resolve_service(registration.registration_id)
        ```

    Lifecycle Management:
        The protocol supports various lifecycle patterns including singleton (one instance),
        transient (new instance each time), scoped (instance per scope), pooled (fixed
        pool of instances), lazy (created on first use), and eager (created at startup).
    """

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
    instance: object
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
    """
    Protocol for dependency graph information.

    Defines the interface for dependency graph analysis including dependency chains,
    circular reference detection, resolution ordering, and depth tracking. This
    protocol enables comprehensive dependency analysis and resolution planning
    across the ONEX ecosystem.

    Attributes:
        service_id: Unique identifier for the service this graph represents
        dependencies: List of service IDs that this service depends on
        dependents: List of service IDs that depend on this service
        depth_level: Depth level in the dependency hierarchy (0 = root level)
        circular_references: List of service IDs involved in circular dependencies
        resolution_order: Optimal order for resolving dependencies
        metadata: Additional graph analysis metadata and configuration

    Example:
        ```python
        @runtime_checkable
        class DependencyGraphImpl:
            service_id: str | None = None
            dependencies: list[str] = ["database", "cache", "auth-service"]
            dependents: list[str] = ["api-gateway", "admin-service"]
            depth_level: int | None = None
            circular_references: list[str] = []
            resolution_order: list[str] = ["database", "auth-service", "cache", "user-service"]
            metadata: dict[str, "ContextValue"] = {"complexity_score": 0.75}

        # Usage in dependency analysis
        graph: ProtocolDependencyGraph = DependencyGraphImpl()
        if graph.circular_references:
            handle_circular_dependencies(graph.circular_references)
        else:
            resolve_in_order(graph.resolution_order)
        ```

    Dependency Analysis:
        The protocol provides comprehensive dependency graph analysis including
        circular reference detection, depth calculation, and optimal resolution
        ordering for robust service dependency management.
    """

    service_id: str
    dependencies: list[str]
    dependents: list[str]
    depth_level: int
    circular_references: list[str]
    resolution_order: list[str]
    metadata: dict[str, "ContextValue"]


@runtime_checkable
class ProtocolInjectionContext(Protocol):
    """
    Protocol for dependency injection context.

    Defines the interface for injection context tracking including resolution status,
    error handling, scope management, and dependency path tracking. This protocol
    enables comprehensive injection context management across the ONEX ecosystem.

    Attributes:
        context_id: Unique identifier for this injection context
        target_service_id: Service ID receiving the injection
        scope: Injection scope for this context
        resolved_dependencies: Dictionary of resolved dependency values
        injection_time: When this injection was performed
        resolution_status: Status of the dependency resolution process
        error_details: Error information if resolution failed
        resolution_path: Path taken to resolve dependencies
        metadata: Additional context metadata and configuration

    Example:
        ```python
        @runtime_checkable
        class InjectionContextImpl:
            context_id: str | None = None
            target_service_id: str | None = None
            scope: LiteralInjectionScope = "request"
            resolved_dependencies: dict[str, "ContextValue"] = {
                "database": db_connection,
                "cache": cache_client
            }
            injection_time: "ProtocolDateTime" = current_time()
            resolution_status: ServiceResolutionStatus = "resolved"
            error_details: str | None = None
            resolution_path: list[str] = ["database", "cache", "auth-service"]
            metadata: dict[str, "ContextValue"] = {"request_id": "req-456"}

        # Usage in injection tracking
        context: ProtocolInjectionContext = InjectionContextImpl()
        if context.resolution_status == "resolved":
            log_successful_injection(context)
        else:
            log_injection_failure(context.error_details)
        ```

    Context Management:
        The protocol provides comprehensive injection context tracking including
        resolution paths, error details, and scope management for robust dependency
        injection debugging and monitoring.
    """

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
    """
    Protocol for service registry status information.

    Defines the interface for comprehensive registry status reporting including
    registration statistics, health monitoring, performance metrics, and distribution
    analysis. This protocol enables robust registry monitoring and operational
    intelligence across the ONEX ecosystem.

    Attributes:
        registry_id: Unique identifier for this registry instance
        status: Overall operational status of the registry
        message: Human-readable status description
        total_registrations: Total number of service registrations
        active_instances: Number of currently active service instances
        failed_registrations: Number of failed service registrations
        circular_dependencies: Number of detected circular dependencies
        lifecycle_distribution: Distribution of services by lifecycle type
        scope_distribution: Distribution of services by injection scope
        health_summary: Health status distribution across all services
        memory_usage_bytes: Current memory usage (if available)
        average_resolution_time_ms: Average dependency resolution time
        last_updated: When this status was last updated

    Example:
        ```python
        @runtime_checkable
        class ServiceRegistryStatusImpl:
            registry_id: str | None = None
            status: LiteralOperationStatus = "operational"
            message: str | None = None
            total_registrations: int | None = None
            active_instances: int | None = None
            failed_registrations: int | None = None
            circular_dependencies: int | None = None
            lifecycle_distribution: dict[LiteralServiceLifecycle, int] = {
                "singleton": 95, "transient": 45, "scoped": 10
            }
            scope_distribution: dict[LiteralInjectionScope, int] = {
                "global": 120, "request": 30
            }
            health_summary: dict[ServiceHealthStatus, int] = {
                "healthy": 140, "degraded": 7, "unhealthy": 3
            }
            memory_usage_bytes: int | None = 4567890
            average_resolution_time_ms: float | None = 2.5
            last_updated: "ProtocolDateTime" = current_time()

        # Usage in monitoring and alerting
        status: ProtocolServiceRegistryStatus = ServiceRegistryStatusImpl()
        if status.circular_dependencies > 0:
            alert_circular_dependencies(status)
        elif status.failed_registrations / status.total_registrations > 0.1:
            alert_high_failure_rate(status)
        ```

    Operational Intelligence:
        The protocol provides comprehensive operational metrics including performance
        monitoring, health tracking, and distribution analysis for registry optimization
        and capacity planning.
    """

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
    """
    Protocol for service validation operations.

    Defines the interface for comprehensive service validation including interface
    compliance checking, dependency validation, and service health verification.
    This protocol enables robust validation workflows across the ONEX ecosystem.

    Methods:
        validate_service: Validate that a service implementation conforms to its interface
        validate_dependencies: Validate that all dependencies can be satisfied

    Example:
        ```python
        @runtime_checkable
        class ServiceValidatorImpl:
            async def validate_service(
                self, service: object, interface: type[object]
            ) -> "ProtocolValidationResult":
                # Check if service implements all required methods
                if not isinstance(service, interface):
                    return ProtocolValidationResult(
                        is_valid=False,
                        errors=[f"Service does not implement {interface.__name__}"]
                    )

                # Validate method signatures and contracts
                method_errors = await self._validate_method_signatures(service, interface)
                if method_errors:
                    return ProtocolValidationResult(
                        is_valid=False,
                        errors=method_errors
                    )

                return ProtocolValidationResult(is_valid=True)

            async def validate_dependencies(
                self, dependencies: list[ProtocolServiceDependency]
            ) -> "ProtocolValidationResult":
                # Validate that all dependencies can be resolved
                unresolved = []
                for dep in dependencies:
                    if not await dep.validate_dependency():
                        unresolved.append(dep.dependency_name)

                if unresolved:
                    return ProtocolValidationResult(
                        is_valid=False,
                        errors=[f"Unresolved dependencies: {', '.join(unresolved)}"]
                    )

                return ProtocolValidationResult(is_valid=True)

        # Usage in service registration
        validator: ProtocolServiceValidator = ServiceValidatorImpl()
        result = await validator.validate_service(implementation, IUserRepository)
        if result.is_valid:
            register_service(implementation)
        else:
            handle_validation_errors(result.errors)
        ```

    Validation Strategies:
        The protocol supports comprehensive validation including interface compliance,
        method signature validation, dependency resolution checking, and service
        health verification for robust service management.
    """

    async def validate_service(
        self, service: object, interface: type[object]
    ) -> "ProtocolValidationResult": ...

    async def validate_dependencies(
        self, dependencies: list["ProtocolServiceDependency"]
    ) -> "ProtocolValidationResult": ...


@runtime_checkable
class ProtocolServiceFactory(Protocol):
    """
    Protocol for service factory operations.

    Defines the interface for service instance creation with dependency injection
    support, context-aware initialization, and lifecycle management. This protocol
    enables robust service creation workflows across the ONEX ecosystem.

    Methods:
        create_instance: Create a new service instance with dependency injection

    Type Parameters:
        T: The type of service instance to create

    Example:
        ```python
        @runtime_checkable
        class ServiceFactoryImpl:
            async def create_instance(
                self, interface: Type[T], context: dict[str, "ContextValue"]
            ) -> T:
                # Resolve dependencies for the requested interface
                dependencies = await self._resolve_dependencies(interface, context)

                # Create instance with dependency injection
                instance = interface(**dependencies)

                # Post-creation initialization if needed
                if hasattr(instance, 'initialize'):
                    await instance.initialize(context)

                return instance

            async def _resolve_dependencies(
                self, interface: type[T], context: dict[str, "ContextValue"]
            ) -> dict[str, object]:
                # Analyze constructor parameters and resolve dependencies
                signature = inspect.signature(interface.__init__)
                dependencies = {}

                for param_name, param in signature.parameters.items():
                    if param_name == 'self':
                        continue

                    # Resolve dependency from context or registry
                    if param_name in context:
                        dependencies[param_name] = context[param_name]
                    else:
                        dependency = await service_registry.resolve(param.annotation)
                        dependencies[param_name] = dependency

                return dependencies

        # Usage in service creation
        factory: ProtocolServiceFactory = ServiceFactoryImpl()
        context: dict[str, "ContextValue"] = {"request_id": "req-123"}

        user_service = await factory.create_instance(IUserService, context)
        repository = await factory.create_instance(IUserRepository, context)
        ```

    Factory Pattern:
        The protocol implements the factory pattern with context-aware dependency
        injection, supporting complex service creation scenarios including constructor
        injection, post-creation initialization, and contextual parameter passing.
    """

    async def create_instance(
        self, interface: type[T], context: dict[str, "ContextValue"]
    ) -> T: ...

    async def dispose_instance(self, instance: object) -> None: ...


@runtime_checkable
class ProtocolServiceRegistryConfig(Protocol):
    """
    Protocol for service registry configuration.

    Defines the interface for comprehensive service registry configuration including
    auto-wiring, lazy loading, dependency detection, monitoring, and performance
    settings. This protocol enables flexible registry configuration across the
    ONEX ecosystem.

    Attributes:
        registry_name: Unique identifier for this registry configuration
        auto_wire_enabled: Whether automatic dependency injection is enabled
        lazy_loading_enabled: Whether services are loaded on first use
        circular_dependency_detection: Whether to detect and handle circular dependencies
        max_resolution_depth: Maximum depth for dependency resolution
        instance_pooling_enabled: Whether instance pooling is enabled for performance
        health_monitoring_enabled: Whether service health monitoring is enabled
        performance_monitoring_enabled: Whether performance metrics collection is enabled
        configuration: Additional configuration parameters and settings

    Example:
        ```python
        @runtime_checkable
        class ServiceRegistryConfigImpl:
            registry_name: str | None = None
            auto_wire_enabled: bool | None = None
            lazy_loading_enabled: bool | None = None
            circular_dependency_detection: bool | None = None
            max_resolution_depth: int | None = None
            instance_pooling_enabled: bool | None = None
            health_monitoring_enabled: bool | None = None
            performance_monitoring_enabled: bool | None = None
            configuration: dict[str, "ContextValue"] = {
                "default_lifecycle": "singleton",
                "default_scope": "global",
                "resolution_timeout": 30.0,
                "health_check_interval": 60.0
            }

        # Usage in registry initialization
        config: ProtocolServiceRegistryConfig = ServiceRegistryConfigImpl()
        registry = ServiceRegistry(config)
        if config.circular_dependency_detection:
            registry.enable_circular_dependency_detection()
        ```

    Configuration Management:
        The protocol supports comprehensive configuration management including
        performance optimization settings, monitoring controls, and behavior
        customization for different deployment environments.
    """

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

    Implements ProtocolRegistryBase[type[TInterface], TImplementation] interface for
    dependency injection service registration and management with advanced lifecycle
    and dependency management features.

    Supports the complete service lifecycle including registration, resolution, injection, and disposal.

    Type Parameters (conceptual):
        K = type[TInterface]: Interface type for service registration
        V = TImplementation: Implementation instance or class

    Core Registry Methods (from ProtocolRegistryBase):
        - register: Maps to register_service (with lifecycle/scope)
        - get: Maps to resolve_service
        - list_keys: Maps to get_all_registrations (lists registration objects)
        - is_registered: Implemented via get_registration check
        - unregister: Maps to unregister_service

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

    Thread Safety:
        Implementations MUST be thread-safe for concurrent read/write operations.

    See Also:
        - ProtocolRegistryBase: Generic base protocol for key-value registries
        - ProtocolServiceRegistrationMetadata: Service registration metadata
        - ProtocolServiceRegistration: Service registration information
    """

    @property
    def config(self) -> ProtocolServiceRegistryConfig: ...

    @property
    def validator(self) -> ProtocolServiceValidator | None: ...

    @property
    def factory(self) -> ProtocolServiceFactory | None: ...

    # Core Registry Methods (ProtocolRegistryBase interface)
    # Note: ProtocolServiceRegistry uses async methods and richer semantics than the base protocol

    def register(
        self,
        key: type[TInterface],
        value: type[TImplementation],
    ) -> None:
        """
        Register a service with default lifecycle (singleton) and scope (global).

        This method provides simplified registration compatible with ProtocolRegistryBase[K, V].
        For advanced registration with lifecycle/scope control, use register_service().

        Args:
            key: Interface type for service registration.
            value: Implementation class for the service.

        Raises:
            RegistryError: If registration fails.
            ValueError: If duplicate key and implementation forbids overwrites.

        Note:
            This is a synchronous wrapper around async register_service with default
            lifecycle='singleton' and scope='global'. For full control, use register_service() directly.
        """
        ...

    def get(self, key: type[TInterface]) -> TInterface:
        """
        Resolve and return a service instance.

        This method provides simplified resolution compatible with ProtocolRegistryBase[K, V].
        For advanced resolution with scope/context control, use resolve_service().

        Args:
            key: Interface type to resolve.

        Returns:
            Service instance implementing the interface.

        Raises:
            KeyError: If interface is not registered.
            RegistryError: If retrieval fails due to internal error.

        Note:
            This is a synchronous wrapper around async resolve_service with default scope.
        """
        ...

    def list_keys(self) -> list[type[TInterface]]:
        """
        List all registered interface types.

        Returns:
            List of interface types that have registrations.
            Order is implementation-specific.

        Thread Safety:
            Must return a consistent snapshot.

        Note:
            This extracts interface types from get_all_registrations() results.
        """
        ...

    def is_registered(self, key: type[TInterface]) -> bool:
        """
        Check if an interface type is registered.

        Args:
            key: Interface type to check.

        Returns:
            True if interface type is registered, False otherwise.

        Thread Safety:
            Result is a point-in-time snapshot.

        Note:
            This checks if get_registrations_by_interface() returns non-empty list.
        """
        ...

    def unregister(self, key: type[TInterface]) -> bool:
        """
        Remove all registrations for an interface type.

        Idempotent operation - safe to call multiple times with same key.

        Args:
            key: Interface type to remove.

        Returns:
            True if any registrations were removed.
            False if no registrations existed (no-op).

        Thread Safety:
            Must be safe to call concurrently with other registry methods.

        Note:
            This removes ALL registrations for the interface. For fine-grained control,
            use unregister_service(registration_id).
        """
        ...

    # Domain-Specific Service Registry Methods
    # These provide rich DI semantics beyond basic key-value registry

    async def register_service(
        self,
        interface: type[TInterface],
        implementation: type[TImplementation],
        lifecycle: LiteralServiceLifecycle,
        scope: LiteralInjectionScope,
        configuration: dict[str, "ContextValue"] | None = None,
    ) -> str: ...

    async def register_instance(
        self,
        interface: type[TInterface],
        instance: TInterface,
        scope: "LiteralInjectionScope" = "global",
        metadata: dict[str, "ContextValue"] | None = None,
    ) -> str: ...

    async def register_factory(
        self,
        interface: type[TInterface],
        factory: "ProtocolServiceFactory",
        lifecycle: "LiteralServiceLifecycle" = "transient",
        scope: "LiteralInjectionScope" = "global",
    ) -> str: ...

    async def unregister_service(self, registration_id: str) -> bool: ...

    async def resolve_service(
        self,
        interface: type[TInterface],
        scope: "LiteralInjectionScope | None" = None,
        context: dict[str, "ContextValue"] | None = None,
    ) -> TInterface: ...

    async def resolve_named_service(
        self,
        interface: type[TInterface],
        name: str,
        scope: "LiteralInjectionScope | None" = None,
    ) -> TInterface: ...

    async def resolve_all_services(
        self, interface: type[TInterface], scope: "LiteralInjectionScope | None" = None
    ) -> list[TInterface]: ...

    async def try_resolve_service(
        self, interface: type[TInterface], scope: "LiteralInjectionScope | None" = None
    ) -> TInterface | None: ...

    async def get_registration(
        self, registration_id: str
    ) -> ProtocolServiceRegistration | None: ...

    async def get_registrations_by_interface(
        self, interface: type[T]
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
