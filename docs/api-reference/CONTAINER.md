# Container Protocols API Reference

## Overview

The ONEX container protocols provide comprehensive dependency injection, service location, and artifact management capabilities for distributed systems. These protocols enable sophisticated service lifecycle management, circular dependency detection, health monitoring, and enterprise-grade dependency injection patterns.

## 🏗️ Protocol Architecture

The container domain consists of **14 specialized protocols** that provide complete dependency injection and artifact management:

### Service Registry Protocol

```python
from omnibase_spi.protocols.container import ProtocolServiceRegistry
from omnibase_spi.protocols.types.protocol_core_types import ContextValue

@runtime_checkable
class ProtocolServiceRegistry(Protocol):
    """
    Service registry protocol for dependency injection and service location.

    Provides comprehensive service lifecycle management with health monitoring,
    scope management, and circular dependency detection.

    Key Features:
        - Service registration with metadata
        - Lifecycle management (singleton, transient, scoped, pooled)
        - Circular dependency detection
        - Health monitoring and validation
        - Factory pattern support
        - Performance metrics collection
    """

    @property
    def config(self) -> ProtocolServiceRegistryConfig: ...

    async def register_service(
        self,
        interface: Type[TInterface],
        implementation: Type[TImplementation],
        lifecycle: LiteralServiceLifecycle,
        scope: LiteralInjectionScope,
        configuration: dict[str, ContextValue] | None = None,
    ) -> str: ...

    async def register_instance(
        self,
        interface: Type[TInterface],
        instance: TInterface,
        scope: LiteralInjectionScope = "global",
        metadata: dict[str, ContextValue] | None = None,
    ) -> str: ...

    async def register_factory(
        self,
        interface: Type[TInterface],
        factory: ProtocolServiceFactory,
        lifecycle: LiteralServiceLifecycle = "transient",
        scope: LiteralInjectionScope = "global",
    ) -> str: ...

    async def resolve_service(
        self,
        interface: Type[TInterface],
        scope: LiteralInjectionScope | None = None,
        context: dict[str, ContextValue] | None = None,
    ) -> TInterface: ...

    async def resolve_named_service(
        self,
        interface: Type[TInterface],
        name: str,
        scope: LiteralInjectionScope | None = None,
    ) -> TInterface: ...

    async def resolve_all_services(
        self, interface: Type[TInterface], scope: LiteralInjectionScope | None = None
    ) -> list[TInterface]: ...

    async def try_resolve_service(
        self, interface: Type[TInterface], scope: LiteralInjectionScope | None = None
    ) -> TInterface | None: ...

    async def get_registration(
        self, registration_id: str
    ) -> ProtocolServiceRegistration | None: ...

    async def get_registrations_by_interface(
        self, interface: Type[T]
    ) -> list[ProtocolServiceRegistration]: ...

    async def get_all_registrations(self) -> list[ProtocolServiceRegistration]: ...

    async def get_active_instances(
        self, registration_id: str | None = None
    ) -> list[ProtocolRegistryServiceInstance]: ...

    async def dispose_instances(
        self, registration_id: str, scope: LiteralInjectionScope | None = None
    ) -> int: ...

    async def validate_registration(
        self, registration: ProtocolServiceRegistration
    ) -> bool: ...

    async def detect_circular_dependencies(
        self, registration: ProtocolServiceRegistration
    ) -> list[str]: ...

    async def get_dependency_graph(
        self, service_id: str
    ) -> ProtocolDependencyGraph | None: ...

    async def get_registry_status(self) -> ProtocolServiceRegistryStatus: ...

    async def validate_service_health(
        self, registration_id: str
    ) -> ProtocolValidationResult: ...

    async def update_service_configuration(
        self, registration_id: str, configuration: dict[str, ContextValue]
    ) -> bool: ...

    async def create_injection_scope(
        self, scope_name: str, parent_scope: str | None = None
    ) -> str: ...

    async def dispose_injection_scope(self, scope_id: str) -> int: ...

    async def get_injection_context(
        self, context_id: str
    ) -> ProtocolInjectionContext | None: ...
```

### Service Registration Protocol

```python
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
    """

    registration_id: str
    service_metadata: ProtocolServiceRegistrationMetadata
    lifecycle: LiteralServiceLifecycle
    scope: LiteralInjectionScope
    dependencies: list[ProtocolServiceDependency]
    registration_status: Literal[
        "registered", "unregistered", "failed", "pending", "conflict", "invalid"
    ]
    health_status: ServiceHealthStatus
    registration_time: ProtocolDateTime
    last_access_time: ProtocolDateTime | None
    access_count: int
    instance_count: int
    max_instances: int | None

    async def validate_registration(self) -> bool: ...

    def is_active(self) -> bool: ...
```

### Service Resolver Protocol

```python
from typing import Protocol, runtime_checkable, Any, TypeVar

T = TypeVar("T")

@runtime_checkable
class ProtocolServiceResolver(Protocol):
    """
    Protocol for service resolution operations.

    Provides service lookup and resolution capabilities for dependency
    injection containers, supporting both protocol-based and name-based
    service resolution patterns.

    Key Features:
        - Type-safe protocol-based resolution
        - String-based service name resolution
        - Support for multiple service implementations
        - Consistent error handling for missing services
        - Integration with service registry patterns
    """

    def get_service(
        self,
        protocol_type_or_name: type[T] | str,
        service_name: str | None = None,
    ) -> Any: ...
```

#### Usage

```python
from omnibase_spi.protocols.container import ProtocolServiceResolver

resolver: ProtocolServiceResolver = get_resolver()

# Protocol type resolution
event_bus = resolver.get_service(ProtocolEventBus)

# String name resolution
cache = resolver.get_service("cache_service")

# Hybrid (type + name)
user_repo = resolver.get_service(ProtocolRepository, "user_repository")
```

### Container Protocol

```python
from typing import Protocol, runtime_checkable, Generic, TypeVar, Any

T = TypeVar("T", covariant=True)

@runtime_checkable
class ProtocolContainer(Protocol, Generic[T]):
    """
    Protocol for generic value containers with metadata.

    Defines the interface for containers that wrap values with associated metadata.
    This protocol enables implementations to provide consistent container behavior
    across different subsystems while maintaining type safety through generics.

    Key Features:
        - Generic type support for any wrapped value type
        - Metadata dictionary for extensible container attributes
        - Type-safe access to wrapped values and metadata
        - Framework-agnostic container abstraction

    Use Cases:
        - Service resolution results with metadata (lifecycle, scope, etc.)
        - Event payloads with routing and tracing information
        - Configuration values with source and validation metadata
        - API responses with headers and status information
        - Tool execution results with performance metrics
    """

    @property
    def value(self) -> T: ...

    @property
    def metadata(self) -> dict[str, Any]: ...

    def get_metadata(self, key: str, default: Any = None) -> Any: ...
```

#### Usage

```python
from omnibase_spi.protocols.container import ProtocolContainer

# Type-safe container usage
container: ProtocolContainer[str] = create_container(
    value="example_data",
    metadata={"source": "api", "timestamp": "2025-01-15T10:30:00Z"}
)

# Access wrapped value (type-safe)
data: str = container.value

# Access metadata
source: str = container.get_metadata("source", "unknown")
all_metadata = container.metadata
```

### Service Factory Protocol

```python
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
    """

    async def create_instance(
        self, interface: Type[T], context: dict[str, ContextValue]
    ) -> T: ...

    async def dispose_instance(self, instance: Any) -> None: ...
```

### Dependency Graph Protocol

```python
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
    """

    service_id: str
    dependencies: list[str]
    dependents: list[str]
    depth_level: int
    circular_references: list[str]
    resolution_order: list[str]
    metadata: dict[str, ContextValue]
```

### Injection Context Protocol

```python
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
    """

    context_id: str
    target_service_id: str
    scope: LiteralInjectionScope
    resolved_dependencies: dict[str, ContextValue]
    injection_time: ProtocolDateTime
    resolution_status: LiteralServiceResolutionStatus
    error_details: str | None
    resolution_path: list[str]
    metadata: dict[str, ContextValue]
```

### Service Registry Status Protocol

```python
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
    last_updated: ProtocolDateTime
```

## 🔧 Type Definitions

### Service Lifecycle Types

```python
LiteralServiceLifecycle = Literal[
    "singleton", "transient", "scoped", "pooled", "lazy", "eager"
]
"""
Service lifecycle patterns for dependency injection.

Values:
    singleton: Single instance shared across all requests
    transient: New instance created for each resolution
    scoped: Instance per scope (request, session, etc.)
    pooled: Fixed pool of instances for performance
    lazy: Created on first use
    eager: Created at startup
"""

LiteralInjectionScope = Literal[
    "request", "session", "thread", "process", "global", "custom"
]
"""
Injection scope patterns for dependency management.

Values:
    request: Per-request scope (web requests)
    session: Per-session scope (user sessions)
    thread: Per-thread scope (threading)
    process: Per-process scope (multiprocessing)
    global: Global scope (application lifetime)
    custom: Custom scope implementation
"""

LiteralServiceResolutionStatus = Literal[
    "resolved", "failed", "circular_dependency", "missing_dependency", "type_mismatch"
]
"""
Service resolution status indicators.

Values:
    resolved: Service successfully resolved
    failed: Resolution failed due to error
    circular_dependency: Circular dependency detected
    missing_dependency: Required dependency not found
    type_mismatch: Type compatibility issue
"""
```

## 🚀 Usage Examples

### Basic Service Registration

```python
from omnibase_spi.protocols.container import ProtocolServiceRegistry
from omnibase_spi.protocols.core import ProtocolLogger

# Register a service
registry: ProtocolServiceRegistry = get_service_registry()

# Register singleton service
registration_id = await registry.register_service(
    interface=ProtocolLogger,
    implementation=ConsoleLogger,
    lifecycle="singleton",
    scope="global"
)

# Resolve service
logger = await registry.resolve_service(ProtocolLogger)
```

### Advanced Dependency Injection

```python
# Register with dependencies
await registry.register_service(
    interface=IUserService,
    implementation=UserService,
    lifecycle="scoped",
    scope="request",
    configuration={
        "timeout": 30,
        "retry_count": 3
    }
)

# Register factory
await registry.register_factory(
    interface=IDatabaseConnection,
    factory=DatabaseConnectionFactory,
    lifecycle="transient",
    scope="request"
)
```

### Health Monitoring

```python
# Check service health
health_result = await registry.validate_service_health(registration_id)

# Get registry status
status = await registry.get_registry_status()
print(f"Active instances: {status.active_instances}")
print(f"Circular dependencies: {status.circular_dependencies}")
```

### Dependency Analysis

```python
# Get dependency graph
graph = await registry.get_dependency_graph("user-service")
if graph.circular_references:
    print(f"Circular dependencies detected: {graph.circular_references}")

# Detect circular dependencies
circular_deps = await registry.detect_circular_dependencies(registration)
```

## 🔍 Implementation Notes

### Lifecycle Management

The container supports various lifecycle patterns:

- **Singleton**: One instance shared across all requests
- **Transient**: New instance created for each resolution
- **Scoped**: Instance per scope (request, session, thread)
- **Pooled**: Fixed pool of instances for performance optimization
- **Lazy**: Created on first use
- **Eager**: Created at startup

### Circular Dependency Detection

The container automatically detects and prevents circular dependencies:

```python
# Automatic detection
circular_deps = await registry.detect_circular_dependencies(registration)

# Dependency graph analysis
graph = await registry.get_dependency_graph(service_id)
if graph.circular_references:
    handle_circular_dependencies(graph.circular_references)
```

### Health Monitoring

Comprehensive health monitoring capabilities:

```python
# Service health validation
health_result = await registry.validate_service_health(registration_id)

# Registry status monitoring
status = await registry.get_registry_status()
if status.circular_dependencies > 0:
    alert_circular_dependencies(status)
```

### Performance Metrics

Built-in performance tracking:

```python
# Registry metrics
status = await registry.get_registry_status()
print(f"Average resolution time: {status.average_resolution_time_ms}ms")
print(f"Memory usage: {status.memory_usage_bytes} bytes")
```

## 📊 Protocol Statistics

- **Total Protocols**: 14 container protocols
- **Service Lifecycle Patterns**: 6 lifecycle types
- **Injection Scopes**: 6 scope patterns
- **Health Monitoring**: Comprehensive status tracking
- **Performance Metrics**: Resolution time and memory usage tracking
- **Dependency Analysis**: Circular dependency detection and graph analysis
- **Container Features**: Generic value containers with metadata support

---

*This API reference is automatically generated from protocol definitions and maintained alongside the codebase.*
