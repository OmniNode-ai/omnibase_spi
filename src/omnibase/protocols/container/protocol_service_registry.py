#!/usr/bin/env python3
"""
Service Registry Protocol - ONEX SPI Interface.

Comprehensive protocol definition for dependency injection service registration and management.
Supports the complete service lifecycle including registration, resolution, injection, and disposal.

Focuses purely on dependency injection patterns rather than artifact or service discovery concerns.
"""

from typing import Any, Literal, Optional, Protocol, Type, TypeVar, runtime_checkable

from omnibase.protocols.types.core_types import (
    ContextValue,
    HealthStatus,
    OperationStatus,
    ProtocolDateTime,
    ProtocolSemVer,
    ProtocolValidationResult,
)

# Generic type for services
T = TypeVar("T")
TInterface = TypeVar("TInterface")
TImplementation = TypeVar("TImplementation")

# Service lifecycle types - using Literal for SPI purity
ServiceLifecycle = Literal[
    "singleton", "transient", "scoped", "pooled", "lazy", "eager"
]


# Service resolution status types
ServiceResolutionStatus = Literal[
    "resolved", "failed", "circular_dependency", "missing_dependency", "type_mismatch"
]

# Dependency injection scope types
InjectionScope = Literal["request", "session", "thread", "process", "global", "custom"]

# Service health status types - using consolidated HealthStatus
ServiceHealthStatus = HealthStatus


@runtime_checkable
class ProtocolServiceMetadata(Protocol):
    """Protocol for service metadata objects."""

    service_id: str
    service_name: str
    service_interface: str
    service_implementation: str
    version: ProtocolSemVer
    description: Optional[str]
    tags: list[str]
    configuration: dict[str, ContextValue]
    created_at: ProtocolDateTime
    last_modified_at: Optional[ProtocolDateTime]


@runtime_checkable
class ProtocolServiceDependency(Protocol):
    """Protocol for service dependency information."""

    dependency_name: str
    dependency_interface: str
    dependency_version: Optional[ProtocolSemVer]
    is_required: bool
    is_circular: bool
    injection_point: str  # constructor, property, method
    default_value: Optional[Any]
    metadata: dict[str, ContextValue]


@runtime_checkable
class ProtocolServiceRegistration(Protocol):
    """Protocol for service registration information."""

    registration_id: str
    service_metadata: ProtocolServiceMetadata
    lifecycle: ServiceLifecycle
    scope: InjectionScope
    dependencies: list[ProtocolServiceDependency]
    registration_status: Literal[
        "registered", "unregistered", "failed", "pending", "conflict", "invalid"
    ]
    health_status: ServiceHealthStatus
    registration_time: ProtocolDateTime
    last_access_time: Optional[ProtocolDateTime]
    access_count: int
    instance_count: int
    max_instances: Optional[int]


@runtime_checkable
class ProtocolServiceInstance(Protocol):
    """Protocol for service instance information."""

    instance_id: str
    service_registration_id: str
    instance: Any
    lifecycle: ServiceLifecycle
    scope: InjectionScope
    created_at: ProtocolDateTime
    last_accessed: ProtocolDateTime
    access_count: int
    is_disposed: bool
    metadata: dict[str, ContextValue]


@runtime_checkable
class ProtocolDependencyGraph(Protocol):
    """Protocol for dependency graph information."""

    service_id: str
    dependencies: list[str]
    dependents: list[str]
    depth_level: int
    circular_references: list[str]
    resolution_order: list[str]
    metadata: dict[str, ContextValue]


@runtime_checkable
class ProtocolInjectionContext(Protocol):
    """Protocol for dependency injection context."""

    context_id: str
    target_service_id: str
    scope: InjectionScope
    resolved_dependencies: dict[str, Any]
    injection_time: ProtocolDateTime
    resolution_status: ServiceResolutionStatus
    error_details: Optional[str]
    resolution_path: list[str]
    metadata: dict[str, ContextValue]


@runtime_checkable
class ProtocolServiceRegistryStatus(Protocol):
    """Protocol for service registry status information."""

    registry_id: str
    status: OperationStatus
    message: str
    total_registrations: int
    active_instances: int
    failed_registrations: int
    circular_dependencies: int
    lifecycle_distribution: dict[ServiceLifecycle, int]
    scope_distribution: dict[InjectionScope, int]
    health_summary: dict[ServiceHealthStatus, int]
    memory_usage_bytes: Optional[int]
    average_resolution_time_ms: Optional[float]
    last_updated: ProtocolDateTime


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
    configuration: dict[str, ContextValue]


@runtime_checkable
class ProtocolServiceValidator(Protocol):
    """Protocol for service validation operations."""

    def validate_registration(self, registration: ProtocolServiceRegistration) -> bool:
        """Validate a service registration."""
        ...

    def validate_dependency_graph(self, graph: ProtocolDependencyGraph) -> list[str]:
        """Validate dependency graph and return validation errors."""
        ...

    def detect_circular_dependencies(self, service_id: str) -> list[str]:
        """Detect circular dependencies for a service."""
        ...


@runtime_checkable
class ProtocolServiceFactory(Protocol):
    """Protocol for service factory operations."""

    def create_instance(
        self,
        registration: ProtocolServiceRegistration,
        context: ProtocolInjectionContext,
    ) -> Any:
        """Create a service instance."""
        ...

    def dispose_instance(self, instance: ProtocolServiceInstance) -> bool:
        """Dispose a service instance."""
        ...


@runtime_checkable
class ProtocolServiceRegistry(Protocol):
    """
    Comprehensive protocol for dependency injection service registry.

    Provides complete service lifecycle management including registration, resolution,
    injection, and disposal. Supports various lifecycle patterns (singleton, transient,
    scoped) and advanced features like circular dependency detection and health monitoring.

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        from typing import Dict, List, Optional, Type, TypeVar
        import asyncio
        from datetime import datetime

        class ServiceRegistryImpl:
            @property
            def config(self) -> ProtocolServiceRegistryConfig: ...

            @property
            def registrations(self) -> dict[str, ProtocolServiceRegistration]: ...

            @property
            def instances(self) -> dict[str, list[ProtocolServiceInstance]]: ...

            @property
            def dependency_graph(self) -> dict[str, ProtocolDependencyGraph]: ...

            async def register_service(
                self,
                interface: Type[TInterface],
                implementation: Type[TImplementation],
                lifecycle: ServiceLifecycle,
                scope: InjectionScope
            ) -> str:
                # Create service metadata
                metadata = ServiceMetadata(
                    service_id=f"{interface.__name__}_{implementation.__name__}",
                    service_name=implementation.__name__,
                    service_interface=interface.__name__,
                    service_implementation=implementation.__name__,
                    version=ProtocolSemVer(1, 0, 0),
                    description=implementation.__doc__,
                    tags=getattr(implementation, '_service_tags', []),
                    configuration={},
                    created_at=datetime.now(),
                    last_modified_at=None
                )

                # Analyze dependencies
                dependencies = await self._analyze_dependencies(implementation)

                # Create registration
                registration = ServiceRegistration(
                    registration_id=metadata.service_id,
                    service_metadata=metadata,
                    lifecycle=lifecycle,
                    scope=scope,
                    dependencies=dependencies,
                    registration_status="registered",
                    health_status="healthy",
                    registration_time=datetime.now(),
                    last_access_time=None,
                    access_count=0,
                    instance_count=0,
                    max_instances=None if lifecycle != "pooled" else 10
                )

                # Validate registration
                if not await self.validate_registration(registration):
                    registration.registration_status = "invalid"
                    raise ValueError(f"Invalid service registration: {metadata.service_id}")

                # Check for circular dependencies
                circular_deps = await self.detect_circular_dependencies(registration)
                if circular_deps:
                    registration.registration_status = "conflict"
                    raise ValueError(f"Circular dependencies detected: {circular_deps}")

                # Store registration
                self.registrations[metadata.service_id] = registration

                # Update dependency graph
                await self._update_dependency_graph(registration)

                return metadata.service_id

            async def resolve_service(
                self,
                interface: Type[TInterface],
                scope: Optional[InjectionScope] = None
            ) -> TInterface:
                # Find matching registration
                registration = await self._find_registration_by_interface(interface)
                if not registration:
                    raise ValueError(f"No registration found for interface: {interface.__name__}")

                # Create injection context
                context = InjectionContext(
                    context_id=f"inject_{registration.registration_id}_{datetime.now().timestamp()}",
                    target_service_id=registration.registration_id,
                    scope=scope or registration.scope,
                    resolved_dependencies={},
                    injection_time=datetime.now(),
                    resolution_status="resolved",
                    error_details=None,
                    resolution_path=[],
                    metadata={}
                )

                # Resolve based on lifecycle
                if registration.lifecycle == "singleton":
                    return await self._resolve_singleton(registration, context)
                elif registration.lifecycle == "transient":
                    return await self._resolve_transient(registration, context)
                elif registration.lifecycle == "scoped":
                    return await self._resolve_scoped(registration, context)
                else:
                    raise ValueError(f"Unsupported lifecycle: {registration.lifecycle}")

            async def _resolve_singleton(
                self,
                registration: ProtocolServiceRegistration,
                context: ProtocolInjectionContext
            ) -> Any:
                # Check if singleton instance exists
                instances = self.instances.get(registration.registration_id, [])
                if instances:
                    instance = instances[0]
                    instance.access_count += 1
                    instance.last_accessed = datetime.now()
                    return instance.instance

                # Create new singleton instance
                service_instance = await self._create_instance(registration, context)
                return service_instance

            async def _create_instance(
                self,
                registration: ProtocolServiceRegistration,
                context: ProtocolInjectionContext
            ) -> Any:
                # Resolve dependencies first
                resolved_deps = {}
                for dep in registration.dependencies:
                    if dep.is_required:
                        dep_interface = self._get_interface_type(dep.dependency_interface)
                        resolved_deps[dep.dependency_name] = await self.resolve_service(dep_interface)

                context.resolved_dependencies = resolved_deps

                # Get implementation class
                impl_class = self._get_implementation_type(
                    registration.service_metadata.service_implementation
                )

                # Create instance with dependency injection
                if resolved_deps:
                    instance = impl_class(**resolved_deps)
                else:
                    instance = impl_class()

                # Create instance metadata
                instance_metadata = ServiceInstance(
                    instance_id=f"{registration.registration_id}_{len(self.instances.get(registration.registration_id, []))}",
                    service_registration_id=registration.registration_id,
                    instance=instance,
                    lifecycle=registration.lifecycle,
                    scope=registration.scope,
                    created_at=datetime.now(),
                    last_accessed=datetime.now(),
                    access_count=1,
                    is_disposed=False,
                    metadata={}
                )

                # Store instance
                if registration.registration_id not in self.instances:
                    self.instances[registration.registration_id] = []
                self.instances[registration.registration_id].append(instance_metadata)

                # Update registration statistics
                registration.instance_count += 1
                registration.last_access_time = datetime.now()
                registration.access_count += 1

                return instance

        # Usage in application
        registry: ProtocolServiceRegistry = ServiceRegistryImpl(config)

        # Define service interfaces
        class IUserRepository(Protocol):
            async def get_user(self, user_id: str) -> User: ...
            async def save_user(self, user: User) -> bool: ...

        class IEmailService(Protocol):
            async def send_email(self, to: str, subject: str, body: str) -> bool: ...

        # Define service implementations
        class DatabaseUserRepository:
            @property
            def db(self) -> Any: ...

            async def get_user(self, user_id: str) -> User:
                # Database operations
                pass

            async def save_user(self, user: User) -> bool:
                # Database operations
                pass

        class SMTPEmailService:
            @property
            def config(self) -> dict[str, Any]: ...

            async def send_email(self, to: str, subject: str, body: str) -> bool:
                # SMTP operations
                pass

        # Register services
        await registry.register_service(
            IUserRepository,
            DatabaseUserRepository,
            lifecycle="singleton",
            scope="global"
        )

        await registry.register_service(
            IEmailService,
            SMTPEmailService,
            lifecycle="transient",
            scope="request"
        )

        # Resolve and use services
        user_repo = await registry.resolve_service(IUserRepository)
        email_service = await registry.resolve_service(IEmailService)

        # Business logic using injected services
        user = await user_repo.get_user("user123")
        await email_service.send_email(
            user.email,
            "Welcome!",
            "Thank you for joining our service."
        )

        # Monitor registry health
        status = await registry.get_registry_status()
        print(f"Registry Status: {status.status}")
        print(f"Active Services: {status.total_registrations}")
        print(f"Active Instances: {status.active_instances}")

        # Dependency graph analysis
        graph = await registry.get_dependency_graph("IUserRepository")
        print(f"Dependencies: {graph.dependencies}")
        print(f"Dependents: {graph.dependents}")

        # Validate service health
        health_report = await registry.validate_service_health("IUserRepository")
        if not health_report.is_healthy:
            print(f"Service health issues: {health_report.issues}")
        ```

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
    def validator(self) -> Optional[ProtocolServiceValidator]:
        """Get service validator."""
        ...

    @property
    def factory(self) -> Optional[ProtocolServiceFactory]:
        """Get service factory."""
        ...

    async def register_service(
        self,
        interface: Type[TInterface],
        implementation: Type[TImplementation],
        lifecycle: ServiceLifecycle,
        scope: InjectionScope,
        configuration: Optional[dict[str, ContextValue]] = None,
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
        scope: InjectionScope = "global",
        metadata: Optional[dict[str, ContextValue]] = None,
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
        factory: ProtocolServiceFactory,
        lifecycle: ServiceLifecycle = "transient",
        scope: InjectionScope = "global",
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
        scope: Optional[InjectionScope] = None,
        context: Optional[dict[str, ContextValue]] = None,
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
        scope: Optional[InjectionScope] = None,
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
        self,
        interface: Type[TInterface],
        scope: Optional[InjectionScope] = None,
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
        self,
        interface: Type[TInterface],
        scope: Optional[InjectionScope] = None,
    ) -> Optional[TInterface]:
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
    ) -> Optional[ProtocolServiceRegistration]:
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
    ) -> list[ProtocolServiceRegistration]:
        """
        Get all registrations for an interface.

        Args:
            interface: Service interface type

        Returns:
            List of service registrations
        """
        ...

    async def get_all_registrations(self) -> list[ProtocolServiceRegistration]:
        """
        Get all service registrations.

        Returns:
            List of all service registrations
        """
        ...

    async def get_active_instances(
        self, registration_id: Optional[str] = None
    ) -> list[ProtocolServiceInstance]:
        """
        Get active service instances.

        Args:
            registration_id: Optional filter by registration ID

        Returns:
            List of active service instances
        """
        ...

    async def dispose_instances(
        self, registration_id: str, scope: Optional[InjectionScope] = None
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
        self, registration: ProtocolServiceRegistration
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
        self, registration: ProtocolServiceRegistration
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
    ) -> Optional[ProtocolDependencyGraph]:
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
        self,
        registration_id: str,
        configuration: dict[str, ContextValue],
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
        self,
        scope_name: str,
        parent_scope: Optional[str] = None,
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
    ) -> Optional[ProtocolInjectionContext]:
        """
        Get injection context information.

        Args:
            context_id: Injection context ID

        Returns:
            Injection context or None if not found
        """
        ...
