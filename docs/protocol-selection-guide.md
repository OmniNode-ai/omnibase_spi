# ONEX Protocol Selection Guide

This guide helps you choose the right protocol for your specific use case within the ONEX ecosystem. Each protocol serves distinct purposes and understanding when to use each one is critical for proper system architecture.

## Quick Reference Matrix

| Use Case | Protocol | When to Use | Key Methods |
|----------|----------|-------------|-------------|
| **Artifact Management** | `ProtocolArtifactContainer` | Managing nodes, tools, contracts, packages | `get_artifacts()`, `get_status()` |
| **Node Discovery** | `ProtocolNodeRegistry` | Distributed node coordination, health monitoring | `register_node()`, `discover_nodes()` |
| **Handler Discovery** | `ProtocolNodeDiscoveryRegistry` | Plugin-based file handler discovery | `discover_and_register_nodes()` |
| **Service Registry** | `ProtocolServiceRegistry` | DI container service management | N/A (info-only protocol) |

## Protocol Categories

### 1. Container & Artifact Management

#### ProtocolArtifactContainer
**Purpose**: Cross-cutting artifact container operations for managing ONEX components.

**When to Use**:
- Loading and managing ONEX nodes, CLI tools, runtimes, adapters
- Checking container health and artifact validity
- Filtering artifacts by type or name
- Building artifact loaders or container implementations

**Key Capabilities**:
```python
from omnibase.protocols.container import ProtocolArtifactContainer

# Artifact management operations
def get_status(self) -> ProtocolArtifactContainerStatus
def get_artifacts(self) -> List[ProtocolArtifactInfo]
def get_artifacts_by_type(self, artifact_type: ContainerArtifactType) -> List[ProtocolArtifactInfo]
def get_artifact_by_name(self, name: str) -> ProtocolArtifactInfo
def has_artifact(self, name: str) -> bool
```

**Artifact Types Supported**:
- `nodes` - ONEX processing nodes
- `cli_tools` - Command-line tools
- `runtimes` - Runtime environments  
- `adapters` - Integration adapters
- `contracts` - YAML contracts
- `packages` - Python packages

**Real-World Example**:
```python
# Use for artifact loader implementations
class NodeArtifactLoader:
    def __init__(self, container: ProtocolArtifactContainer):
        self.container = container
    
    def load_compute_nodes(self):
        # Get all node artifacts
        nodes = self.container.get_artifacts_by_type("nodes")
        
        # Filter for compute nodes
        compute_nodes = [
            node for node in nodes 
            if node.metadata.get("node_type") == "compute"
        ]
        return compute_nodes
```

### 2. Node Discovery & Registration

#### ProtocolNodeRegistry
**Purpose**: Distributed node discovery and registration with health monitoring.

**When to Use**:
- Building distributed ONEX systems with multiple environments
- Implementing Consul-based or etcd-based node discovery
- Node health monitoring and heartbeat management
- Group Gateway pattern implementation
- Cross-environment node coordination

**Key Capabilities**:
```python
from omnibase.protocols.core import ProtocolNodeRegistry

# Node lifecycle management
async def register_node(self, node_info: ProtocolNodeInfo, ttl_seconds: int = 30) -> bool
async def unregister_node(self, node_id: str) -> bool
async def heartbeat(self, node_id: str) -> bool

# Node discovery and querying
async def discover_nodes(self, node_type: Optional[NodeType] = None, 
                        environment: Optional[str] = None,
                        group: Optional[str] = None) -> List[ProtocolNodeInfo]
async def get_gateway_for_group(self, group: str) -> Optional[ProtocolNodeInfo]

# Real-time monitoring
async def watch_node_changes(self, callback: ProtocolNodeChangeCallback) -> ProtocolWatchHandle
```

**Environment & Group Support**:
- **Environment Isolation**: `dev`, `staging`, `prod` boundaries
- **Node Groups**: Independent mini-meshes for tool groups
- **Health Monitoring**: TTL-based health checks with automatic cleanup
- **Service Discovery**: Consul/etcd backend integration

**Real-World Example**:
```python
# Use for distributed orchestrator implementations
class DistributedOrchestrator:
    def __init__(self, registry: ProtocolNodeRegistry, environment: str = "prod"):
        self.registry = registry
        self.environment = environment
    
    async def scale_compute_group(self, target_count: int):
        # Discover current compute nodes
        compute_nodes = await self.registry.discover_nodes(
            node_type="COMPUTE",
            environment=self.environment,
            group="processing"
        )
        
        current_count = len([n for n in compute_nodes if n.health_status == "healthy"])
        
        if current_count < target_count:
            await self._spawn_additional_nodes(target_count - current_count)
```

#### ProtocolNodeDiscoveryRegistry  
**Purpose**: Plugin-based discovery and registration of file type handlers.

**When to Use**:
- Building extensible file processing systems
- Implementing plugin architectures for file handlers
- Dynamic handler discovery from entry points, config files, environment variables
- Supporting multiple handler discovery sources simultaneously

**Key Capabilities**:
```python
from omnibase.protocols.discovery import ProtocolNodeDiscoveryRegistry

# Discovery source management
def register_discovery_source(self, discovery: ProtocolHandlerDiscovery) -> None
def discover_and_register_nodes(self) -> None

# Handler registration
def register_node_info(self, node_info: ProtocolHandlerInfo) -> None
```

**Discovery Sources Supported**:
- **Entry Points**: Python setuptools entry points
- **Configuration Files**: YAML/JSON configuration-based discovery
- **Environment Variables**: Runtime environment-based registration
- **Directory Scanning**: Filesystem-based discovery

**Real-World Example**:
```python
# Use for building extensible file processing engines
class ExtensibleFileProcessor:
    def __init__(self):
        self.registry: ProtocolNodeDiscoveryRegistry = NodeDiscoveryRegistryImpl()
        
        # Register multiple discovery sources
        self.registry.register_discovery_source(EntryPointDiscovery("onex.handlers"))
        self.registry.register_discovery_source(ConfigFileDiscovery("config/handlers.yaml"))
        self.registry.register_discovery_source(EnvironmentDiscovery("ONEX_HANDLER_"))
        
        # Discover all available handlers
        self.registry.discover_and_register_nodes()
```

### 3. Service Management

#### ProtocolServiceRegistry
**Purpose**: Information-only protocol for service registry metadata.

**When to Use**:
- Dependency injection container implementations
- Service registry status reporting
- Monitoring service registration statistics
- Building service registry dashboards

**Protocol Definition**:
```python
from omnibase.protocols.types.container_types import ProtocolServiceRegistry

class ProtocolServiceRegistry(Protocol):
    registry_id: str
    total_services: int
    active_services: int
    last_updated: float
```

**Real-World Example**:
```python
# Use for monitoring service registry health
class ServiceRegistryMonitor:
    def __init__(self, registry: ProtocolServiceRegistry):
        self.registry = registry
    
    def get_health_metrics(self):
        return {
            "registry_id": self.registry.registry_id,
            "service_count": self.registry.total_services,
            "active_ratio": self.registry.active_services / self.registry.total_services,
            "last_update_age": time.time() - self.registry.last_updated
        }
```

## Decision Tree

### Step 1: Identify Your Domain

```
Are you working with...?

├── Artifact Management (nodes, tools, contracts)
│   └── Use: ProtocolArtifactContainer
│
├── Distributed Node Coordination
│   └── Use: ProtocolNodeRegistry
│
├── File Handler Plugin System
│   └── Use: ProtocolNodeDiscoveryRegistry
│
└── Service Registry Information
    └── Use: ProtocolServiceRegistry
```

### Step 2: Consider Your Architecture Pattern

#### Container-Based Architecture
```python
# For artifact-centric systems
container: ProtocolArtifactContainer = ArtifactLoaderNode()
nodes = container.get_artifacts_by_type("nodes")
```

#### Discovery-Based Architecture  
```python
# For distributed systems
registry: ProtocolNodeRegistry = ConsulNodeRegistry("prod")
nodes = await registry.discover_nodes(node_type="COMPUTE")
```

#### Plugin-Based Architecture
```python
# For extensible handler systems
registry: ProtocolNodeDiscoveryRegistry = HandlerRegistryImpl()
registry.discover_and_register_nodes()
```

## Integration Patterns

### Multi-Protocol Composition
Many real-world systems use multiple protocols together:

```python
class ComprehensiveNodeManager:
    def __init__(self):
        # Artifact management
        self.container: ProtocolArtifactContainer = NodeArtifactContainer()
        
        # Distributed coordination
        self.node_registry: ProtocolNodeRegistry = ConsulNodeRegistry()
        
        # Handler discovery
        self.handler_registry: ProtocolNodeDiscoveryRegistry = HandlerRegistry()
    
    async def initialize_system(self):
        # 1. Load artifacts from container
        available_nodes = self.container.get_artifacts_by_type("nodes")
        
        # 2. Register nodes for distributed discovery
        for node_artifact in available_nodes:
            node_info = self._create_node_info(node_artifact)
            await self.node_registry.register_node(node_info)
        
        # 3. Discover and register file handlers
        self.handler_registry.discover_and_register_nodes()
```

### Environment-Specific Protocol Selection

```python
# Development environment - use simple container
if environment == "dev":
    container: ProtocolArtifactContainer = LocalArtifactContainer()

# Production environment - use distributed registry  
elif environment == "prod":
    registry: ProtocolNodeRegistry = ConsulNodeRegistry("prod", "consul.company.com:8500")
    
    # Register with high availability settings
    await registry.register_node(node_info, ttl_seconds=60)
```

## Best Practices

### 1. Protocol Selection Principles

**Single Responsibility**: Choose protocols that match your specific use case rather than trying to force one protocol to handle multiple concerns.

**Environment Awareness**: Consider whether you need local-only operations (`ProtocolArtifactContainer`) or distributed coordination (`ProtocolNodeRegistry`).

**Extensibility Requirements**: Use discovery protocols (`ProtocolNodeDiscoveryRegistry`) when you need plugin-based architecture.

### 2. Common Anti-Patterns

❌ **Don't use `ProtocolNodeRegistry` for simple artifact loading**
```python
# Wrong - overengineered for local artifact access
registry: ProtocolNodeRegistry = ConsulNodeRegistry()
# Just to get local file handlers
```

✅ **Do use `ProtocolArtifactContainer` for local artifact management**  
```python
# Right - appropriate for local container operations
container: ProtocolArtifactContainer = LocalArtifactContainer()
handlers = container.get_artifacts_by_type("nodes")
```

❌ **Don't use `ProtocolArtifactContainer` for distributed service discovery**
```python
# Wrong - container can't discover remote nodes
container: ProtocolArtifactContainer = SomeContainer()
# Won't find nodes on other machines
```

✅ **Do use `ProtocolNodeRegistry` for distributed discovery**
```python
# Right - designed for distributed node coordination
registry: ProtocolNodeRegistry = ConsulNodeRegistry()
nodes = await registry.discover_nodes(node_type="COMPUTE", environment="prod")
```

### 3. Performance Considerations

- **`ProtocolArtifactContainer`**: Fast local operations, good for startup artifact loading
- **`ProtocolNodeRegistry`**: Network latency for discovery, use caching for frequently accessed data
- **`ProtocolNodeDiscoveryRegistry`**: One-time discovery cost, cache results for performance

### 4. Testing Strategies

Each protocol type benefits from different testing approaches:

```python
# Mock artifact containers for testing
class MockArtifactContainer:
    def __init__(self, test_artifacts: List[ProtocolArtifactInfo]):
        self.artifacts = test_artifacts
    
    def get_artifacts(self) -> List[ProtocolArtifactInfo]:
        return self.artifacts

# Mock registries for distributed testing
class MockNodeRegistry:
    def __init__(self):
        self.nodes = {}
    
    async def register_node(self, node_info: ProtocolNodeInfo) -> bool:
        self.nodes[node_info.node_id] = node_info
        return True
```

## Conclusion

Choose protocols based on your specific architectural needs:

- **Local artifact management** → `ProtocolArtifactContainer`
- **Distributed node coordination** → `ProtocolNodeRegistry` 
- **Plugin-based handler discovery** → `ProtocolNodeDiscoveryRegistry`
- **Service registry monitoring** → `ProtocolServiceRegistry`

When in doubt, start with the simplest protocol that meets your needs and evolve to more complex protocols as your requirements grow.