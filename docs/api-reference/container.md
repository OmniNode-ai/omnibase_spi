# Container Protocols API Reference

## Overview

The ONEX container protocols provide comprehensive dependency injection, service location, and artifact management capabilities for distributed systems. These protocols enable sophisticated service lifecycle management, circular dependency detection, health monitoring, and enterprise-grade dependency injection patterns.

## Protocol Architecture

The container domain consists of specialized protocols that provide complete dependency injection and artifact management:

### Service Registry Protocol

```python
from omnibase_spi.protocols.container import ProtocolServiceRegistry
from omnibase_spi.protocols.types.core_types import ServiceMetadata, HealthStatus

@runtime_checkable
class ProtocolServiceRegistry(Protocol):
    """
    Service registry protocol for dependency injection and service location.

    Provides comprehensive service lifecycle management with health monitoring,
    scope management, and circular dependency detection.

    Features:
        - Service registration with metadata
        - Lifecycle management (singleton, transient, scoped)
        - Circular dependency detection
        - Health monitoring and validation
        - Factory pattern support
        - Performance metrics collection
    """

    async def register_service(
        self,
        service_type: type,
        implementation: Any,
        scope: ServiceScope = ServiceScope.SINGLETON,
        metadata: Optional[ServiceMetadata] = None
    ) -> str:
        """
        Register service implementation with the container.

        Args:
            service_type: Protocol or abstract base class type
            implementation: Concrete implementation instance or factory
            scope: Service lifecycle scope management
            metadata: Additional service metadata

        Returns:
            Registration ID for service management

        Raises:
            RegistrationError: If service registration fails
            CircularDependencyError: If circular dependency detected
        """
        ...

    async def get_service(self, service_type: type) -> Any:
        """
        Resolve service instance from the container.

        Args:
            service_type: Protocol or service interface type

        Returns:
            Service implementation instance

        Raises:
            ServiceNotFoundError: If service not registered
            ResolutionError: If service resolution fails
        """
        ...

    async def get_all_services(self, service_type: type) -> List[Any]:
        """
        Get all registered implementations of a service type.

        Useful for plugin patterns and multi-implementation scenarios.
        """
        ...

    async def check_service_health(self, service_type: type) -> HealthStatus:
        """
        Check health status of registered service.

        Returns detailed health information including dependencies.
        """
        ...

    async def unregister_service(self, service_type: type) -> bool:
        """
        Unregister service and clean up resources.

        Handles dependency cleanup and lifecycle management.
        """
        ...
```

### Artifact Container Protocol

```python
from omnibase_spi.protocols.container import ProtocolArtifactContainer
from omnibase_spi.protocols.types.core_types import ArtifactMetadata, ArtifactStatus

@runtime_checkable
class ProtocolArtifactContainer(Protocol):
    """
    Artifact container protocol for managing code artifacts and resources.

    Provides type-based discovery, status monitoring, and lifecycle
    management for artifacts, plugins, and resources.

    Features:
        - Type-based artifact discovery
        - Status monitoring and validation
        - Lifecycle management
        - Resource cleanup
        - Plugin loading patterns
        - Artifact dependencies
    """

    async def add_artifact(
        self,
        artifact_id: str,
        artifact_data: Any,
        artifact_type: str,
        metadata: Optional[ArtifactMetadata] = None
    ) -> bool:
        """
        Add artifact to the container.

        Args:
            artifact_id: Unique identifier for artifact
            artifact_data: Artifact content or reference
            artifact_type: Type/category of artifact
            metadata: Additional artifact metadata

        Returns:
            Success status of artifact addition

        Raises:
            ArtifactExistsError: If artifact ID already exists
            ValidationError: If artifact data is invalid
        """
        ...

    async def get_artifact(
        self,
        artifact_id: str
    ) -> Tuple[Any, ArtifactMetadata]:
        """
        Retrieve artifact by ID.

        Returns:
            Tuple of (artifact_data, metadata)

        Raises:
            ArtifactNotFoundError: If artifact doesn't exist
        """
        ...

    async def find_artifacts_by_type(
        self,
        artifact_type: str
    ) -> List[Tuple[str, Any, ArtifactMetadata]]:
        """
        Find all artifacts of specified type.

        Returns:
            List of (artifact_id, artifact_data, metadata) tuples
        """
        ...

    async def get_artifact_status(self, artifact_id: str) -> ArtifactStatus:
        """
        Get current status of artifact.

        Returns detailed status including health and dependencies.
        """
        ...

    async def remove_artifact(self, artifact_id: str) -> bool:
        """
        Remove artifact and clean up resources.

        Handles dependency cleanup and lifecycle management.
        """
        ...

    async def list_artifact_types(self) -> List[str]:
        """Get list of all registered artifact types."""
        ...
```

## Type Definitions

### Core Container Types

```python
from omnibase_spi.protocols.types.container_types import (
    ServiceScope,
    ServiceMetadata,
    ArtifactMetadata,
    ArtifactStatus,
    DependencyGraph
)

# Service lifecycle scopes
class ServiceScope(Enum):
    """Service lifecycle management scopes."""
    SINGLETON = "singleton"      # Single instance across application
    TRANSIENT = "transient"      # New instance each time
    SCOPED = "scoped"           # Instance per scope (request, session, etc.)
    LAZY_SINGLETON = "lazy_singleton"  # Singleton created on first access

@dataclass
class ServiceMetadata:
    """
    Metadata for registered services.

    Attributes:
        name: Human-readable service name
        version: Service version for compatibility
        dependencies: List of required service types
        health_check_interval: Health check frequency in seconds
        tags: Service tags for discovery and filtering
        priority: Registration priority for multiple implementations
        factory_function: Optional factory function name
    """
    name: str
    version: str = "1.0.0"
    dependencies: List[type] = field(default_factory=list)
    health_check_interval: int = 30
    tags: List[str] = field(default_factory=list)
    priority: int = 0
    factory_function: Optional[str] = None

@dataclass
class ArtifactMetadata:
    """
    Metadata for container artifacts.

    Attributes:
        name: Human-readable artifact name
        version: Artifact version
        created_at: Creation timestamp
        size_bytes: Artifact size in bytes
        checksum: Content checksum for integrity
        dependencies: List of required artifacts
        tags: Artifact tags for discovery
    """
    name: str
    version: str
    created_at: str
    size_bytes: int
    checksum: str
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

class ArtifactStatus(Enum):
    """Artifact status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOADING = "loading"
    ERROR = "error"
    DEPRECATED = "deprecated"
```

### Dependency Graph Types

```python
@dataclass
class DependencyNode:
    """Node in the dependency graph."""
    service_type: type
    implementation: Any
    scope: ServiceScope
    dependencies: List[type]
    dependents: List[type]
    health_status: HealthStatus

@dataclass
class DependencyGraph:
    """
    Complete dependency graph for circular dependency detection.

    Attributes:
        nodes: Map of service type to dependency node
        resolution_order: Topologically sorted resolution order
        circular_dependencies: Detected circular dependencies
    """
    nodes: Dict[type, DependencyNode]
    resolution_order: List[type]
    circular_dependencies: List[List[type]]
```

## Usage Patterns

### Basic Service Registration

```python
from omnibase_spi.protocols.container import ProtocolServiceRegistry
from omnibase_spi.protocols.event_bus import ProtocolEventBus

async def setup_basic_dependency_injection(
    registry: ProtocolServiceRegistry
) -> None:
    """Set up basic dependency injection with protocols."""

    # Register concrete implementations
    event_bus_impl = KafkaEventBusImplementation()
    await registry.register_service(
        service_type=ProtocolEventBus,
        implementation=event_bus_impl,
        scope=ServiceScope.SINGLETON,
        metadata=ServiceMetadata(
            name="Kafka Event Bus",
            version="1.0.0",
            tags=["messaging", "kafka"],
            health_check_interval=30
        )
    )

    # Register factory-created services
    async def create_workflow_processor() -> WorkflowProcessor:
        event_bus = await registry.get_service(ProtocolEventBus)
        return WorkflowProcessor(event_bus=event_bus)

    await registry.register_service(
        service_type=WorkflowProcessor,
        implementation=create_workflow_processor,
        scope=ServiceScope.TRANSIENT,
        metadata=ServiceMetadata(
            name="Workflow Processor",
            dependencies=[ProtocolEventBus],
            factory_function="create_workflow_processor"
        )
    )
```

### Service Resolution with Health Monitoring

```python
async def resolve_services_with_health_monitoring(
    registry: ProtocolServiceRegistry
) -> None:
    """Resolve services with comprehensive health monitoring."""

    # Get service instance
    event_bus = await registry.get_service(ProtocolEventBus)

    # Check service health before use
    health_status = await registry.check_service_health(ProtocolEventBus)

    if health_status != HealthStatus.HEALTHY:
        # Handle unhealthy service
        await handle_service_health_issue(ProtocolEventBus, health_status)
        return

    # Use service safely
    await event_bus.publish_event(create_test_event())

    # Get all implementations (useful for plugin patterns)
    all_processors = await registry.get_all_services(WorkflowProcessor)
    for processor in all_processors:
        await processor.process_workflow(workflow_data)
```

### Artifact Management

```python
from omnibase_spi.protocols.container import ProtocolArtifactContainer

async def manage_plugin_artifacts(
    container: ProtocolArtifactContainer
) -> None:
    """Manage plugin artifacts with lifecycle control."""

    # Add plugin artifact
    plugin_code = load_plugin_from_file("user_plugin.py")
    success = await container.add_artifact(
        artifact_id="user_plugin_v1",
        artifact_data=plugin_code,
        artifact_type="python_plugin",
        metadata=ArtifactMetadata(
            name="User Management Plugin",
            version="1.0.0",
            created_at=datetime.utcnow().isoformat(),
            size_bytes=len(plugin_code.encode()),
            checksum=calculate_checksum(plugin_code),
            tags=["plugin", "user_management"]
        )
    )

    if not success:
        raise RuntimeError("Failed to add plugin artifact")

    # Find all plugins
    plugins = await container.find_artifacts_by_type("python_plugin")
    for plugin_id, plugin_code, metadata in plugins:
        # Load and validate plugin
        status = await container.get_artifact_status(plugin_id)
        if status == ArtifactStatus.ACTIVE:
            await load_and_execute_plugin(plugin_code)

    # Clean up old plugins
    await container.remove_artifact("old_plugin_v0_9")
```

## Advanced Features

### Circular Dependency Detection

```python
async def implement_circular_dependency_detection(
    registry: ProtocolServiceRegistry
) -> None:
    """Implement circular dependency detection and resolution."""

    class ServiceA(Protocol):
        def method_a(self) -> str: ...

    class ServiceB(Protocol):
        def method_b(self) -> str: ...

    # This would create a circular dependency
    class ServiceAImpl:
        def __init__(self, service_b: ServiceB):
            self.service_b = service_b

    class ServiceBImpl:
        def __init__(self, service_a: ServiceA):
            self.service_a = service_a

    try:
        # Register services with circular dependencies
        await registry.register_service(
            ServiceA,
            ServiceAImpl,
            metadata=ServiceMetadata(dependencies=[ServiceB])
        )

        await registry.register_service(
            ServiceB,
            ServiceBImpl,
            metadata=ServiceMetadata(dependencies=[ServiceA])
        )

    except CircularDependencyError as e:
        # Handle circular dependency
        logger.error(f"Circular dependency detected: {e.dependency_chain}")

        # Implement resolution strategy (e.g., lazy injection)
        await resolve_circular_dependency_with_lazy_injection(e)
```

### Factory Pattern Implementation

```python
async def implement_factory_patterns(
    registry: ProtocolServiceRegistry
) -> None:
    """Implement factory patterns for complex service creation."""

    class DatabaseConnectionFactory:
        """Factory for database connections with environment-specific configuration."""

        def __init__(self, config: DatabaseConfig):
            self.config = config

        async def create_connection(self) -> DatabaseConnection:
            """Create database connection based on environment."""
            if self.config.environment == "prod":
                return ProductionDatabaseConnection(self.config)
            elif self.config.environment == "staging":
                return StagingDatabaseConnection(self.config)
            else:
                return DevelopmentDatabaseConnection(self.config)

    # Register factory
    db_factory = DatabaseConnectionFactory(db_config)
    await registry.register_service(
        service_type=DatabaseConnection,
        implementation=db_factory.create_connection,
        scope=ServiceScope.SCOPED,  # New connection per scope
        metadata=ServiceMetadata(
            name="Database Connection Factory",
            factory_function="create_connection"
        )
    )

    # Register services that depend on factory-created instances
    async def create_user_repository() -> UserRepository:
        db_connection = await registry.get_service(DatabaseConnection)
        return UserRepository(db_connection)

    await registry.register_service(
        UserRepository,
        create_user_repository,
        scope=ServiceScope.SINGLETON,
        metadata=ServiceMetadata(dependencies=[DatabaseConnection])
    )
```

### Scope Management

```python
async def implement_scope_management(
    registry: ProtocolServiceRegistry
) -> None:
    """Implement advanced scope management for different contexts."""

    class RequestScopedService:
        """Service that maintains state per request."""

        def __init__(self, request_id: str):
            self.request_id = request_id
            self.state = {}

    class ScopeManager:
        """Manages service scopes and lifecycle."""

        def __init__(self, registry: ProtocolServiceRegistry):
            self.registry = registry
            self.scoped_instances: Dict[str, Dict[type, Any]] = {}

        async def create_request_scope(self, request_id: str) -> Dict[type, Any]:
            """Create new request scope with scoped services."""
            scope_instances = {}

            # Create scoped service instance for this request
            scoped_service = RequestScopedService(request_id)
            scope_instances[RequestScopedService] = scoped_service

            self.scoped_instances[request_id] = scope_instances
            return scope_instances

        async def cleanup_request_scope(self, request_id: str) -> None:
            """Clean up request scope and dispose resources."""
            if request_id in self.scoped_instances:
                scope_instances = self.scoped_instances[request_id]

                # Dispose of scoped services
                for service_instance in scope_instances.values():
                    if hasattr(service_instance, 'dispose'):
                        await service_instance.dispose()

                del self.scoped_instances[request_id]

    # Register scoped service
    scope_manager = ScopeManager(registry)

    async def get_request_scoped_service(request_id: str) -> RequestScopedService:
        scope_instances = await scope_manager.create_request_scope(request_id)
        return scope_instances[RequestScopedService]

    # Use in request handling
    async def handle_request(request_id: str) -> None:
        scoped_service = await get_request_scoped_service(request_id)
        # ... process request with scoped service
        await scope_manager.cleanup_request_scope(request_id)
```

## Integration with Other Domains

### Event Bus Integration

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBus

async def integrate_container_with_event_bus(
    registry: ProtocolServiceRegistry,
    event_bus: ProtocolEventBus
) -> None:
    """Integrate container lifecycle events with event bus."""

    # Publish service registration events
    async def publish_service_registered_event(
        service_type: type,
        registration_id: str
    ) -> None:
        event = EventMessage(
            event_id=str(uuid4()),
            event_type="service.registered",
            payload={
                "service_type": service_type.__name__,
                "registration_id": registration_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            metadata=EventMetadata(
                source="service_registry",
                correlation_id=str(uuid4())
            ),
            timestamp=datetime.utcnow().isoformat()
        )

        await event_bus.publish_event(event, target_topic="service_events")

    # Monitor service health and publish health events
    async def monitor_service_health() -> None:
        """Monitor all registered services and publish health events."""
        while True:
            # Get all registered service types
            for service_type in await registry.get_registered_service_types():
                health_status = await registry.check_service_health(service_type)

                if health_status != HealthStatus.HEALTHY:
                    await publish_service_health_event(service_type, health_status)

            await asyncio.sleep(30)  # Check every 30 seconds

    # Start health monitoring
    asyncio.create_task(monitor_service_health())
```

### MCP Tool Registry Integration

```python
from omnibase_spi.protocols.mcp import ProtocolMCPRegistry

async def integrate_container_with_mcp_registry(
    registry: ProtocolServiceRegistry,
    mcp_registry: ProtocolMCPRegistry
) -> None:
    """Integrate container services with MCP tool registry."""

    # Register MCP tools as container services
    mcp_tools = await mcp_registry.list_available_tools()

    for tool_definition in mcp_tools:
        # Create service wrapper for MCP tool
        tool_service = MCPToolService(
            tool_definition=tool_definition,
            mcp_registry=mcp_registry
        )

        # Register as container service
        await registry.register_service(
            service_type=type(f"MCPTool_{tool_definition.name}", (), {}),
            implementation=tool_service,
            scope=ServiceScope.SINGLETON,
            metadata=ServiceMetadata(
                name=f"MCP Tool: {tool_definition.name}",
                tags=["mcp_tool", tool_definition.tool_type],
                dependencies=[ProtocolMCPRegistry]
            )
        )

    # Enable container services to use MCP tools
    async def create_service_with_mcp_tools() -> ComplexService:
        """Create service that uses MCP tools via container."""
        search_tool = await registry.get_service(MCPTool_semantic_search)
        analyze_tool = await registry.get_service(MCPTool_analyze)

        return ComplexService(
            search_tool=search_tool,
            analyze_tool=analyze_tool
        )
```

## Testing Strategies

### Protocol Compliance Testing

```python
import pytest
from omnibase_spi.protocols.container import ProtocolServiceRegistry

class TestServiceRegistryCompliance:
    """Test suite for service registry protocol compliance."""

    @pytest.fixture
    def service_registry(self) -> ProtocolServiceRegistry:
        """Provide service registry implementation for testing."""
        return MockServiceRegistryImplementation()

    async def test_service_registration(
        self,
        service_registry: ProtocolServiceRegistry
    ):
        """Test service registration and resolution."""

        # Register service
        test_service = TestServiceImplementation()
        registration_id = await service_registry.register_service(
            service_type=TestService,
            implementation=test_service,
            scope=ServiceScope.SINGLETON
        )

        assert registration_id is not None

        # Resolve service
        resolved_service = await service_registry.get_service(TestService)
        assert resolved_service is test_service

    async def test_circular_dependency_detection(
        self,
        service_registry: ProtocolServiceRegistry
    ):
        """Test circular dependency detection."""

        with pytest.raises(CircularDependencyError):
            # Register services with circular dependencies
            await service_registry.register_service(
                ServiceA,
                ServiceAImpl,
                metadata=ServiceMetadata(dependencies=[ServiceB])
            )

            await service_registry.register_service(
                ServiceB,
                ServiceBImpl,
                metadata=ServiceMetadata(dependencies=[ServiceA])
            )

    async def test_health_monitoring(
        self,
        service_registry: ProtocolServiceRegistry
    ):
        """Test service health monitoring."""

        # Register healthy service
        healthy_service = HealthyTestService()
        await service_registry.register_service(
            TestService,
            healthy_service,
            metadata=ServiceMetadata(health_check_interval=1)
        )

        # Check initial health
        health_status = await service_registry.check_service_health(TestService)
        assert health_status == HealthStatus.HEALTHY

        # Simulate service failure
        healthy_service.simulate_failure()

        # Wait for health check
        await asyncio.sleep(2)

        # Check degraded health
        health_status = await service_registry.check_service_health(TestService)
        assert health_status == HealthStatus.UNHEALTHY
```

### Integration Testing

```python
class TestContainerIntegration:
    """Test container integration with other domains."""

    async def test_event_bus_integration(self):
        """Test container integration with event bus."""

        # Set up integrated system
        registry = MockServiceRegistry()
        event_bus = MockEventBus()

        # Register event bus as service
        await registry.register_service(ProtocolEventBus, event_bus)

        # Register service that depends on event bus
        await registry.register_service(
            EventDrivenService,
            lambda: EventDrivenServiceImpl(
                event_bus=registry.get_service(ProtocolEventBus)
            )
        )

        # Resolve and test integrated service
        service = await registry.get_service(EventDrivenService)
        await service.publish_test_event()

        # Verify event was published
        assert len(event_bus.published_events) == 1
```

## Performance Optimization

### Service Resolution Caching

```python
async def implement_service_resolution_caching(
    registry: ProtocolServiceRegistry
) -> None:
    """Implement caching for service resolution performance."""

    class CachedServiceRegistry:
        """Service registry wrapper with resolution caching."""

        def __init__(self, base_registry: ProtocolServiceRegistry):
            self.base_registry = base_registry
            self.resolution_cache: Dict[type, Any] = {}
            self.cache_ttl: Dict[type, float] = {}

        async def get_service(self, service_type: type) -> Any:
            """Get service with caching for singletons."""

            # Check cache for singleton services
            if service_type in self.resolution_cache:
                cache_time = self.cache_ttl.get(service_type, 0)
                if time.time() - cache_time < 300:  # 5 minute TTL
                    return self.resolution_cache[service_type]

            # Resolve from base registry
            service = await self.base_registry.get_service(service_type)

            # Cache singleton services
            service_info = await self.base_registry.get_service_info(service_type)
            if service_info.scope == ServiceScope.SINGLETON:
                self.resolution_cache[service_type] = service
                self.cache_ttl[service_type] = time.time()

            return service

        async def invalidate_cache(self, service_type: type) -> None:
            """Invalidate cached service resolution."""
            if service_type in self.resolution_cache:
                del self.resolution_cache[service_type]
                del self.cache_ttl[service_type]
```

### Batch Service Registration

```python
async def implement_batch_service_registration(
    registry: ProtocolServiceRegistry
) -> None:
    """Implement batch service registration for performance."""

    class BatchRegistration:
        """Batch service registration for performance."""

        def __init__(self, registry: ProtocolServiceRegistry):
            self.registry = registry
            self.batch_registrations: List[ServiceRegistration] = []

        def add_registration(
            self,
            service_type: type,
            implementation: Any,
            scope: ServiceScope = ServiceScope.SINGLETON,
            metadata: Optional[ServiceMetadata] = None
        ) -> None:
            """Add service registration to batch."""
            self.batch_registrations.append(
                ServiceRegistration(
                    service_type=service_type,
                    implementation=implementation,
                    scope=scope,
                    metadata=metadata or ServiceMetadata(name=service_type.__name__)
                )
            )

        async def commit_batch(self) -> List[str]:
            """Commit all batched registrations."""
            registration_ids = []

            # Register all services in batch
            for registration in self.batch_registrations:
                registration_id = await self.registry.register_service(
                    service_type=registration.service_type,
                    implementation=registration.implementation,
                    scope=registration.scope,
                    metadata=registration.metadata
                )
                registration_ids.append(registration_id)

            self.batch_registrations.clear()
            return registration_ids

    # Usage example
    batch = BatchRegistration(registry)

    # Add multiple services to batch
    batch.add_registration(ProtocolEventBus, KafkaEventBus())
    batch.add_registration(ProtocolMCPRegistry, MCPRegistryImpl())
    batch.add_registration(WorkflowProcessor, WorkflowProcessorImpl())

    # Commit all registrations at once
    registration_ids = await batch.commit_batch()
    logger.info(f"Registered {len(registration_ids)} services in batch")
```

## Configuration and Deployment

### Container Configuration

```python
@dataclass
class ContainerConfiguration:
    """Configuration for container deployment."""

    # Performance settings
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    max_cached_services: int = 1000

    # Health monitoring
    health_check_interval: int = 30
    unhealthy_threshold: int = 3
    health_check_timeout: int = 5

    # Dependency management
    enable_circular_dependency_detection: bool = True
    max_dependency_depth: int = 10
    lazy_initialization: bool = False

    # Artifact management
    max_artifact_size_mb: int = 100
    artifact_retention_days: int = 30
    enable_artifact_compression: bool = True

    # Monitoring and metrics
    enable_metrics: bool = True
    metrics_port: int = 8082
    enable_tracing: bool = True

async def create_container_from_config(
    config: ContainerConfiguration
) -> Tuple[ProtocolServiceRegistry, ProtocolArtifactContainer]:
    """Create container implementations from configuration."""

    service_registry = ServiceRegistryImplementation(
        enable_caching=config.enable_caching,
        cache_ttl=config.cache_ttl_seconds,
        health_check_interval=config.health_check_interval,
        enable_circular_dependency_detection=config.enable_circular_dependency_detection
    )

    artifact_container = ArtifactContainerImplementation(
        max_artifact_size=config.max_artifact_size_mb * 1024 * 1024,
        retention_days=config.artifact_retention_days,
        enable_compression=config.enable_artifact_compression
    )

    return service_registry, artifact_container
```

## Best Practices

### Container Design Guidelines

1. **Service Lifecycle**: Use appropriate scopes (singleton, transient, scoped) based on service requirements
2. **Dependency Management**: Detect and resolve circular dependencies early in development
3. **Health Monitoring**: Implement comprehensive health checks for all critical services  
4. **Resource Cleanup**: Always implement proper disposal for scoped and transient services
5. **Performance**: Use caching for frequently resolved singleton services
6. **Type Safety**: Always register services with their protocol interfaces, not concrete types
7. **Metadata**: Include comprehensive metadata for service discovery and monitoring

### Error Handling

1. **Registration Errors**: Handle service registration failures gracefully
2. **Resolution Errors**: Provide meaningful error messages for service resolution failures
3. **Health Failures**: Implement fallback strategies for unhealthy services
4. **Resource Leaks**: Ensure proper cleanup of resources in all lifecycle phases

The container protocols provide enterprise-grade dependency injection and artifact management capabilities that form the backbone of service coordination in the ONEX distributed orchestration framework.
