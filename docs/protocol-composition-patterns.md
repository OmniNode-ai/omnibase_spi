# ONEX Protocol Composition Patterns

This guide demonstrates how to compose multiple ONEX protocols together to build complex, scalable systems. Protocol composition enables building sophisticated architectures while maintaining clean separation of concerns.

## Core Composition Principles

### 1. Separation of Concerns
Each protocol handles a specific domain:
- **ProtocolArtifactContainer**: Manages local artifacts (nodes, tools, contracts)
- **ProtocolNodeRegistry**: Coordinates distributed nodes across environments
- **ProtocolNodeDiscoveryRegistry**: Discovers and registers file handlers dynamically
- **ProtocolServiceRegistry**: Provides service registry metadata and monitoring

### 2. Layered Architecture
Protocols compose in layers from local to distributed:

```
┌─────────────────────────────────────┐
│ Application Layer                   │
├─────────────────────────────────────┤
│ ProtocolServiceRegistry             │ ← Service monitoring
├─────────────────────────────────────┤
│ ProtocolNodeRegistry                │ ← Distributed coordination
├─────────────────────────────────────┤
│ ProtocolNodeDiscoveryRegistry       │ ← Handler discovery
├─────────────────────────────────────┤
│ ProtocolArtifactContainer           │ ← Local artifact management
└─────────────────────────────────────┘
```

### 3. Protocol Interaction Patterns
- **Sequential**: Load artifacts → Discover handlers → Register nodes → Monitor services
- **Parallel**: Independent protocol operations for performance
- **Hierarchical**: Higher-level protocols depend on lower-level ones
- **Event-Driven**: Protocols respond to changes in other protocols

## Basic Composition Patterns

### Pattern 1: Local Development Stack

**Use Case**: Single-machine development with local file processing

```python
from omnibase_spi.protocols.container import ProtocolArtifactContainer
from omnibase_spi.protocols.discovery import ProtocolNodeDiscoveryRegistry

class LocalDevelopmentStack:
    """Simple composition for local development."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path

        # Layer 1: Local artifact management
        self.container: ProtocolArtifactContainer = LocalArtifactContainer(workspace_path)

        # Layer 2: Handler discovery for file processing
        self.handler_registry: ProtocolNodeDiscoveryRegistry = LocalHandlerRegistry()

    def initialize(self):
        """Initialize development stack."""
        # 1. Load local artifacts
        status = self.container.get_status()
        print(f"Loaded {status.artifact_count} artifacts")

        # 2. Discover file handlers from local sources
        self._setup_local_discovery()
        self.handler_registry.discover_and_register_nodes()

        # 3. Validate system is ready
        self._validate_system()

    def _setup_local_discovery(self):
        """Setup discovery sources for local development."""
        # Discover from entry points
        entry_discovery = EntryPointDiscovery("onex.dev.handlers")
        self.handler_registry.register_discovery_source(entry_discovery)

        # Discover from local config
        config_path = self.workspace_path / "config" / "handlers.yaml"
        config_discovery = ConfigFileDiscovery(str(config_path))
        self.handler_registry.register_discovery_source(config_discovery)

    def _validate_system(self):
        """Validate system initialization."""
        nodes = self.container.get_artifacts_by_type("nodes")
        if len(nodes) == 0:
            raise RuntimeError("No processing nodes found")

        print(f"Development stack ready: {len(nodes)} nodes available")

# Usage
dev_stack = LocalDevelopmentStack(Path("/workspace/onex-dev"))
dev_stack.initialize()
```

### Pattern 2: Distributed Production Stack

**Use Case**: Multi-node production system with service coordination

```python
from omnibase_spi.protocols.core import ProtocolNodeRegistry
from omnibase_spi.protocols.container import ProtocolArtifactContainer
from omnibase_spi.protocols.discovery import ProtocolNodeDiscoveryRegistry
from omnibase_spi.protocols.types.container_types import ProtocolServiceRegistry

class DistributedProductionStack:
    """Full-featured composition for production deployment."""

    def __init__(self, environment: str = "prod"):
        self.environment = environment

        # Layer 1: Local artifact management
        self.container: ProtocolArtifactContainer = ProductionArtifactContainer()

        # Layer 2: Handler discovery
        self.handler_registry: ProtocolNodeDiscoveryRegistry = ProductionHandlerRegistry()

        # Layer 3: Distributed node coordination  
        self.node_registry: ProtocolNodeRegistry = ConsulNodeRegistry(
            environment=environment,
            consul_endpoint="consul.company.com:8500"
        )

        # Layer 4: Service monitoring
        self.service_registry: ProtocolServiceRegistry = ServiceRegistryMonitor()

    async def initialize(self):
        """Initialize production stack with proper sequencing."""

        # Phase 1: Local preparation
        await self._prepare_local_components()

        # Phase 2: Distributed registration
        await self._register_with_cluster()

        # Phase 3: Start monitoring
        await self._start_monitoring()

    async def _prepare_local_components(self):
        """Prepare local artifacts and handlers."""
        print("Preparing local components...")

        # 1. Load and validate artifacts
        status = self.container.get_status()
        if status.status != "ACTIVE":
            raise RuntimeError(f"Artifact container not ready: {status.message}")

        # 2. Setup comprehensive handler discovery
        self._setup_production_discovery()

        # 3. Discover and register handlers
        self.handler_registry.discover_and_register_nodes()

        # 4. Validate critical artifacts are available
        compute_nodes = self.container.get_artifacts_by_type("nodes")
        if len(compute_nodes) == 0:
            raise RuntimeError("No compute nodes available for production")

        print(f"Local preparation complete: {len(compute_nodes)} compute nodes ready")

    def _setup_production_discovery(self):
        """Setup production-grade discovery sources."""
        # Entry points for installed packages
        entry_discovery = EntryPointDiscovery("onex.prod.handlers")
        self.handler_registry.register_discovery_source(entry_discovery)

        # Production configuration
        config_discovery = ConfigFileDiscovery("/etc/onex/handlers.yaml")
        self.handler_registry.register_discovery_source(config_discovery)

        # Environment-based discovery for runtime configuration
        env_discovery = EnvironmentDiscovery("ONEX_PROD_HANDLER_")
        self.handler_registry.register_discovery_source(env_discovery)

        # Kubernetes ConfigMap discovery (if available)
        if self._is_kubernetes_environment():
            k8s_discovery = KubernetesHandlerDiscovery("onex-handlers")
            self.handler_registry.register_discovery_source(k8s_discovery)

    async def _register_with_cluster(self):
        """Register this node with the distributed cluster."""
        print("Registering with distributed cluster...")

        # Create node information from artifacts
        node_info = self._create_node_info()

        # Register with longer TTL for production stability
        success = await self.node_registry.register_node(node_info, ttl_seconds=120)
        if not success:
            raise RuntimeError("Failed to register with cluster")

        # Start heartbeat process
        asyncio.create_task(self._heartbeat_loop(node_info.node_id))

        print(f"Registered as {node_info.node_id} in {self.environment} environment")

    async def _start_monitoring(self):
        """Start monitoring and health checks."""
        print("Starting monitoring systems...")

        # Start node change monitoring
        await self.node_registry.watch_node_changes(
            callback=self._handle_node_changes,
            group="processing"
        )

        # Start service registry monitoring
        asyncio.create_task(self._monitor_service_health())

        print("Monitoring systems active")

    async def _heartbeat_loop(self, node_id: str):
        """Maintain heartbeat with cluster."""
        while True:
            try:
                await self.node_registry.heartbeat(node_id)
                await asyncio.sleep(30)  # 30-second heartbeat
            except Exception as e:
                print(f"Heartbeat failed: {e}")
                # Implement exponential backoff retry logic
                await asyncio.sleep(60)

    async def _handle_node_changes(self, node_info: ProtocolNodeInfo, change_type: str):
        """Handle changes in cluster nodes."""
        if change_type == "unhealthy":
            print(f"Node {node_info.node_name} became unhealthy - implementing failover")
            await self._handle_node_failure(node_info)
        elif change_type == "new":
            print(f"New node joined: {node_info.node_name}")
            await self._handle_new_node(node_info)

# Usage
production_stack = DistributedProductionStack("prod")
await production_stack.initialize()
```

## Advanced Composition Patterns

### Pattern 3: Multi-Environment Orchestrator

**Use Case**: Managing multiple environments with centralized orchestration

```python
class MultiEnvironmentOrchestrator:
    """Orchestrates multiple environments using protocol composition."""

    def __init__(self, environments: List[str] = ["dev", "staging", "prod"]):
        self.environments = environments
        self.environment_stacks = {}

        # Central artifact management
        self.central_container: ProtocolArtifactContainer = CentralArtifactContainer()

        # Per-environment registries
        for env in environments:
            self.environment_stacks[env] = {
                'node_registry': ConsulNodeRegistry(environment=env),
                'handler_registry': EnvironmentHandlerRegistry(env),
                'service_registry': EnvironmentServiceRegistry(env)
            }

    async def deploy_to_environment(self, environment: str, artifact_name: str):
        """Deploy artifact to specific environment using coordinated protocols."""

        # 1. Get artifact from central container
        artifact = self.central_container.get_artifact_by_name(artifact_name)

        # 2. Get environment-specific registries
        stack = self.environment_stacks[environment]
        node_registry = stack['node_registry']
        handler_registry = stack['handler_registry']

        # 3. Discover target nodes in environment
        target_nodes = await node_registry.discover_nodes(
            node_type="COMPUTE",
            environment=environment,
            health_filter="healthy"
        )

        if len(target_nodes) == 0:
            raise RuntimeError(f"No healthy compute nodes in {environment}")

        # 4. Deploy to each target node
        deployment_results = []
        for node in target_nodes:
            result = await self._deploy_to_node(artifact, node, handler_registry)
            deployment_results.append(result)

        # 5. Validate deployment success
        success_count = sum(1 for r in deployment_results if r.success)
        print(f"Deployed {artifact_name} to {success_count}/{len(target_nodes)} nodes in {environment}")

        return deployment_results

    async def _deploy_to_node(self, artifact: ProtocolArtifactInfo,
                            node: ProtocolNodeInfo,
                            handler_registry: ProtocolNodeDiscoveryRegistry):
        """Deploy artifact to specific node."""
        try:
            # Create node-specific handler info
            handler_info = self._create_handler_info(artifact, node)

            # Register handler on target node
            handler_registry.register_node_info(handler_info)

            return DeploymentResult(node_id=node.node_id, success=True)
        except Exception as e:
            return DeploymentResult(node_id=node.node_id, success=False, error=str(e))
```

### Pattern 4: Event-Driven Composition

**Use Case**: Reactive system where protocols respond to changes in other protocols

```python
class EventDrivenComposition:
    """Event-driven protocol composition with reactive updates."""

    def __init__(self):
        # Core protocols
        self.container: ProtocolArtifactContainer = ObservableArtifactContainer()
        self.node_registry: ProtocolNodeRegistry = ConsulNodeRegistry()
        self.handler_registry: ProtocolNodeDiscoveryRegistry = ReactiveHandlerRegistry()

        # Event coordination
        self.event_bus = EventBus()
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Setup reactive event handlers between protocols."""

        # React to artifact changes
        self.event_bus.subscribe("artifact.added", self._on_artifact_added)
        self.event_bus.subscribe("artifact.removed", self._on_artifact_removed)

        # React to node changes
        self.event_bus.subscribe("node.registered", self._on_node_registered)
        self.event_bus.subscribe("node.unhealthy", self._on_node_unhealthy)

        # React to handler discovery
        self.event_bus.subscribe("handler.discovered", self._on_handler_discovered)

    async def _on_artifact_added(self, event: ArtifactEvent):
        """React to new artifacts being added."""
        artifact = event.artifact

        if artifact.artifact_type == "nodes":
            # New node artifact - register with cluster
            node_info = self._create_node_info_from_artifact(artifact)
            await self.node_registry.register_node(node_info)

        elif artifact.artifact_type == "contracts":
            # New contract - trigger handler rediscovery
            self.handler_registry.discover_and_register_nodes()

    async def _on_node_registered(self, event: NodeEvent):
        """React to nodes being registered."""
        node_info = event.node_info

        # Check if new node needs handlers
        if node_info.node_type == "COMPUTE":
            # Deploy relevant handlers to new compute node
            await self._deploy_handlers_to_node(node_info)

    async def _on_node_unhealthy(self, event: NodeEvent):
        """React to nodes becoming unhealthy."""
        unhealthy_node = event.node_info

        # Find replacement nodes
        replacement_nodes = await self.node_registry.discover_nodes(
            node_type=unhealthy_node.node_type,
            group=unhealthy_node.group,
            health_filter="healthy"
        )

        # Redistribute workload
        await self._redistribute_workload(unhealthy_node, replacement_nodes)

    async def _deploy_handlers_to_node(self, node_info: ProtocolNodeInfo):
        """Deploy appropriate handlers to a new node."""
        # Get available handlers
        available_handlers = self.handler_registry.get_discovered_handlers()

        # Filter handlers appropriate for this node type
        node_handlers = [
            handler for handler in available_handlers
            if self._handler_compatible_with_node(handler, node_info)
        ]

        # Deploy handlers
        for handler in node_handlers:
            await self._deploy_handler(handler, node_info)
```

### Pattern 5: Hierarchical Service Composition

**Use Case**: Building services that compose multiple protocols hierarchically

```python
class HierarchicalServiceComposition:
    """Hierarchical composition with service dependencies."""

    def __init__(self):
        # Base layer: Artifact and handler management
        self.base_layer = BaseServiceLayer()

        # Coordination layer: Node registry and discovery
        self.coordination_layer = CoordinationServiceLayer(self.base_layer)

        # Application layer: Business logic services
        self.application_layer = ApplicationServiceLayer(self.coordination_layer)

    async def start_services(self):
        """Start services in hierarchical order."""
        await self.base_layer.start()
        await self.coordination_layer.start()
        await self.application_layer.start()

class BaseServiceLayer:
    """Foundation layer with artifacts and handlers."""

    def __init__(self):
        self.container: ProtocolArtifactContainer = ArtifactContainerService()
        self.handler_registry: ProtocolNodeDiscoveryRegistry = HandlerRegistryService()

    async def start(self):
        """Start base services."""
        # 1. Initialize artifact container
        container_status = self.container.get_status()
        if container_status.status != "ACTIVE":
            raise RuntimeError("Artifact container failed to start")

        # 2. Discover and register handlers
        self.handler_registry.discover_and_register_nodes()

        print("Base layer started successfully")

class CoordinationServiceLayer:
    """Coordination layer with distributed services."""

    def __init__(self, base_layer: BaseServiceLayer):
        self.base_layer = base_layer
        self.node_registry: ProtocolNodeRegistry = DistributedNodeRegistry()
        self.service_registry: ProtocolServiceRegistry = ServiceRegistryService()

    async def start(self):
        """Start coordination services."""
        # 1. Create node info from base layer artifacts
        artifacts = self.base_layer.container.get_artifacts_by_type("nodes")

        # 2. Register each node with distributed registry
        for artifact in artifacts:
            node_info = self._create_node_info(artifact)
            await self.node_registry.register_node(node_info)

        print("Coordination layer started successfully")

class ApplicationServiceLayer:
    """Application layer with business services."""

    def __init__(self, coordination_layer: CoordinationServiceLayer):
        self.coordination_layer = coordination_layer
        self.business_services = []

    async def start(self):
        """Start application services."""
        # 1. Get available compute nodes
        compute_nodes = await self.coordination_layer.node_registry.discover_nodes(
            node_type="COMPUTE",
            health_filter="healthy"
        )

        # 2. Start business services on compute nodes
        for node in compute_nodes:
            service = self._create_business_service(node)
            await service.start()
            self.business_services.append(service)

        print(f"Application layer started: {len(self.business_services)} services")
```

## Integration Patterns

### Pattern 6: Cross-Protocol Data Flow

**Use Case**: Data flowing between different protocol domains

```python
class CrossProtocolDataFlow:
    """Demonstrates data flow across protocol boundaries."""

    def __init__(self):
        self.container: ProtocolArtifactContainer = ArtifactContainer()
        self.node_registry: ProtocolNodeRegistry = NodeRegistry()
        self.handler_registry: ProtocolNodeDiscoveryRegistry = HandlerRegistry()

    async def process_file_with_coordination(self, file_path: Path):
        """Process file using coordinated protocols."""

        # 1. Find appropriate handler from artifact container
        handlers = self.container.get_artifacts_by_type("nodes")
        suitable_handler = self._find_handler_for_file(handlers, file_path)

        # 2. Find healthy compute nodes for processing
        compute_nodes = await self.node_registry.discover_nodes(
            node_type="COMPUTE",
            health_filter="healthy"
        )

        if not compute_nodes:
            raise RuntimeError("No healthy compute nodes available")

        # 3. Select optimal node based on load and capabilities
        optimal_node = self._select_optimal_node(compute_nodes, suitable_handler)

        # 4. Process file on selected node
        result = await self._process_on_node(file_path, suitable_handler, optimal_node)

        # 5. Update handler registry with processing statistics
        self._update_handler_stats(suitable_handler, result)

        return result

    def _find_handler_for_file(self, handlers: List[ProtocolArtifactInfo],
                              file_path: Path) -> ProtocolArtifactInfo:
        """Find best handler for file type."""
        file_ext = file_path.suffix.lower()

        for handler in handlers:
            supported_extensions = handler.metadata.get("extensions", [])
            if file_ext in supported_extensions:
                return handler

        raise ValueError(f"No handler found for {file_ext} files")

    def _select_optimal_node(self, nodes: List[ProtocolNodeInfo],
                           handler: ProtocolArtifactInfo) -> ProtocolNodeInfo:
        """Select optimal node for processing."""
        # Consider node load, capabilities, and proximity
        scored_nodes = []

        for node in nodes:
            score = 0

            # Prefer nodes with lower load
            current_load = node.metadata.get("cpu_usage", 100)
            score += (100 - current_load) / 100 * 0.4

            # Prefer nodes with required capabilities
            required_memory = handler.metadata.get("memory_required", 1000)
            available_memory = node.metadata.get("memory_mb", 0)
            if available_memory >= required_memory:
                score += 0.3

            # Prefer nodes in same availability zone
            handler_zone = handler.metadata.get("preferred_zone", "")
            node_zone = node.metadata.get("zone", "")
            if handler_zone == node_zone:
                score += 0.3

            scored_nodes.append((node, score))

        # Return highest scoring node
        return max(scored_nodes, key=lambda x: x[1])[0]
```

## Performance Optimization Patterns

### Pattern 7: Caching and Lazy Loading

```python
class OptimizedComposition:
    """Performance-optimized protocol composition."""

    def __init__(self):
        # Lazy-loaded protocols
        self._container: Optional[ProtocolArtifactContainer] = None
        self._node_registry: Optional[ProtocolNodeRegistry] = None

        # Caching
        self._artifact_cache = {}
        self._node_cache = {}
        self._cache_ttl = 300  # 5 minutes

    @property
    def container(self) -> ProtocolArtifactContainer:
        """Lazy-loaded artifact container."""
        if self._container is None:
            self._container = ArtifactContainer()
        return self._container

    @property  
    def node_registry(self) -> ProtocolNodeRegistry:
        """Lazy-loaded node registry."""
        if self._node_registry is None:
            self._node_registry = NodeRegistry()
        return self._node_registry

    def get_cached_artifacts(self, artifact_type: str) -> List[ProtocolArtifactInfo]:
        """Get artifacts with caching."""
        cache_key = f"artifacts:{artifact_type}"

        # Check cache
        if cache_key in self._artifact_cache:
            cached_data, timestamp = self._artifact_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_data

        # Cache miss - fetch from container
        artifacts = self.container.get_artifacts_by_type(artifact_type)
        self._artifact_cache[cache_key] = (artifacts, time.time())

        return artifacts

    async def get_cached_nodes(self, node_type: str, environment: str) -> List[ProtocolNodeInfo]:
        """Get nodes with caching."""
        cache_key = f"nodes:{node_type}:{environment}"

        # Check cache
        if cache_key in self._node_cache:
            cached_data, timestamp = self._node_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_data

        # Cache miss - fetch from registry
        nodes = await self.node_registry.discover_nodes(
            node_type=node_type,
            environment=environment
        )
        self._node_cache[cache_key] = (nodes, time.time())

        return nodes
```

## Error Handling and Resilience Patterns

### Pattern 8: Circuit Breaker Composition

```python
class ResilientComposition:
    """Resilient protocol composition with circuit breaker pattern."""

    def __init__(self):
        self.container: ProtocolArtifactContainer = ArtifactContainer()
        self.node_registry: ProtocolNodeRegistry = NodeRegistry()

        # Circuit breakers for each protocol
        self.container_breaker = CircuitBreaker(failure_threshold=3, timeout=60)
        self.registry_breaker = CircuitBreaker(failure_threshold=5, timeout=120)

    async def robust_node_discovery(self, node_type: str) -> List[ProtocolNodeInfo]:
        """Node discovery with circuit breaker protection."""

        try:
            # Try distributed discovery first
            return await self.registry_breaker.call(
                self.node_registry.discover_nodes,
                node_type=node_type
            )

        except CircuitBreakerOpen:
            print("Node registry circuit breaker open - falling back to local artifacts")

            # Fallback to local artifacts
            try:
                artifacts = await self.container_breaker.call(
                    self.container.get_artifacts_by_type,
                    "nodes"
                )

                # Convert artifacts to node info
                return [self._artifact_to_node_info(a) for a in artifacts]

            except CircuitBreakerOpen:
                print("All circuit breakers open - using cached fallback")
                return self._get_cached_fallback_nodes(node_type)

    def _get_cached_fallback_nodes(self, node_type: str) -> List[ProtocolNodeInfo]:
        """Final fallback using cached node information."""
        # Return minimal node info from local cache
        return self._local_node_cache.get(node_type, [])
```

## Best Practices for Protocol Composition

### 1. Initialization Order
Always initialize protocols in dependency order:
1. **ProtocolArtifactContainer** (local artifacts)
2. **ProtocolNodeDiscoveryRegistry** (handler discovery)  
3. **ProtocolNodeRegistry** (distributed coordination)
4. **ProtocolServiceRegistry** (monitoring)

### 2. Error Handling
```python
async def safe_protocol_initialization():
    """Safe initialization with proper error handling."""
    try:
        # Initialize in dependency order
        container = await initialize_container()
        handler_registry = await initialize_handlers(container)
        node_registry = await initialize_nodes(handler_registry)
        service_registry = await initialize_monitoring(node_registry)

        return ProtocolStack(container, handler_registry, node_registry, service_registry)

    except ArtifactContainerError:
        # Critical - cannot proceed without local artifacts
        raise RuntimeError("Failed to initialize artifact container")

    except HandlerDiscoveryError:
        # Warning - can continue with reduced functionality  
        logger.warning("Handler discovery failed - some file types may not be supported")

    except NodeRegistryError:
        # Info - single-node mode
        logger.info("Node registry unavailable - running in single-node mode")
```

### 3. Resource Management
```python
class ManagedProtocolComposition:
    """Protocol composition with proper resource management."""

    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_protocols()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self._cleanup_protocols()

    async def _cleanup_protocols(self):
        """Clean up protocol resources."""
        # Stop monitoring first
        if hasattr(self.node_registry, 'stop_watch'):
            await self.node_registry.stop_watch(self.watch_handle)

        # Unregister from distributed systems
        if hasattr(self.node_registry, 'unregister_node'):
            await self.node_registry.unregister_node(self.node_id)

        # Close local resources
        if hasattr(self.container, 'close'):
            await self.container.close()

# Usage with resource management
async with ManagedProtocolComposition() as composition:
    await composition.process_workload()
    # Automatic cleanup on exit
```

## Testing Composition Patterns

### Integration Testing
```python
class TestProtocolComposition:
    """Test protocol composition patterns."""

    @pytest.fixture
    async def composition_stack(self):
        """Create test composition stack."""
        container = MockArtifactContainer()
        handler_registry = MockHandlerRegistry()
        node_registry = MockNodeRegistry()

        stack = ProtocolComposition(container, handler_registry, node_registry)
        await stack.initialize()

        yield stack

        await stack.cleanup()

    async def test_artifact_to_node_flow(self, composition_stack):
        """Test data flow from artifacts to node registration."""

        # 1. Add artifact to container
        test_artifact = create_test_artifact("compute_node")
        composition_stack.container.add_artifact(test_artifact)

        # 2. Trigger node registration from artifact
        await composition_stack.register_artifact_as_node(test_artifact)

        # 3. Verify node was registered
        nodes = await composition_stack.node_registry.discover_nodes(
            node_type="COMPUTE"
        )

        assert len(nodes) == 1
        assert nodes[0].node_name == test_artifact.name

    async def test_composition_resilience(self, composition_stack):
        """Test composition behavior under failure conditions."""

        # Simulate node registry failure
        composition_stack.node_registry.set_failure_mode(True)

        # Should fallback to local artifacts
        nodes = await composition_stack.robust_node_discovery("COMPUTE")

        # Should still return results from local container
        assert len(nodes) > 0
```

Protocol composition enables building sophisticated, scalable ONEX systems while maintaining clean architecture and separation of concerns. Choose composition patterns based on your specific deployment and operational requirements.
