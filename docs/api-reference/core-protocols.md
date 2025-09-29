# Core Protocols API Reference

## Overview

The ONEX core protocols provide fundamental system-level capabilities for the distributed orchestration framework. These protocols enable caching services, node registry operations, configuration management, workflow reduction patterns, and essential system utilities that form the backbone of the ONEX architecture.

## Protocol Architecture

The core domain consists of system-level protocols that provide essential distributed system capabilities:

### Cache Service Protocol

```python
from omnibase_spi.protocols.core import ProtocolCacheService, ProtocolCacheServiceProvider
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

@runtime_checkable
class ProtocolCacheService(Protocol, Generic[T]):
    """
    Protocol for cache service operations.

    Generic cache service supporting any serializable value type with
    comprehensive caching capabilities including TTL, statistics, and
    pattern-based operations.

    Features:
        - Generic type-safe caching for any serializable value
        - TTL-based cache expiration management
        - Pattern-based cache operations for bulk management
        - Cache statistics and performance monitoring
        - Backend-agnostic implementation support (Redis, in-memory, etc.)
        - Existence checking without value retrieval
    """

    async def get(self, key: str) -> Optional[T]:
        """
        Retrieve cached data by key.

        Args:
            key: Cache key to retrieve

        Returns:
            Cached data of type T, or None if not found or expired

        Raises:
            CacheError: If cache operation fails
        """
        ...

    async def set(self, key: str, value: T, ttl_seconds: Optional[int] = None) -> bool:
        """
        Store data in cache with optional TTL.

        Args:
            key: Cache key to store under
            value: Data to cache (must be serializable)
            ttl_seconds: Time to live in seconds, None for default/no expiration

        Returns:
            True if successfully cached, False otherwise

        Raises:
            CacheError: If cache operation fails
            SerializationError: If value cannot be serialized
        """
        ...

    async def delete(self, key: str) -> bool:
        """
        Delete cached data by key.

        Args:
            key: Cache key to delete

        Returns:
            True if key existed and was deleted, False if key didn't exist

        Raises:
            CacheError: If cache operation fails
        """
        ...

    async def clear(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache entries, optionally by pattern.

        Args:
            pattern: Optional glob-style pattern to match keys for deletion
                    (e.g., "user:*", "session:*:data"). If None, clears all entries.

        Returns:
            Number of entries cleared

        Raises:
            CacheError: If cache operation fails
        """
        ...

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache without retrieving value.

        Efficient existence check that doesn't trigger deserialization
        or data transfer for large cached values.

        Args:
            key: Cache key to check

        Returns:
            True if key exists and is not expired, False otherwise

        Raises:
            CacheError: If cache operation fails
        """
        ...

    def get_stats(self) -> "ProtocolCacheStatistics":
        """
        Get comprehensive cache statistics.

        Returns:
            ProtocolCacheStatistics with hit ratios, memory usage, operation counts, etc.

        Raises:
            CacheError: If statistics collection fails
        """
        ...

@runtime_checkable
class ProtocolCacheServiceProvider(Protocol, Generic[T]):
    """Protocol for cache service provider/factory."""

    def create_cache_service(self) -> ProtocolCacheService[T]:
        """
        Create cache service instance.

        Returns:
            ProtocolCacheService implementation for type T

        Raises:
            ConfigurationError: If cache service cannot be configured
        """
        ...

    def get_cache_configuration(self) -> dict[str, ContextValue]:
        """
        Get cache configuration parameters.

        Returns:
            Dictionary with cache configuration including connection strings,
            timeouts, pool sizes, etc.
        """
        ...
```

### Node Registry Protocol

```python
from omnibase_spi.protocols.core import ProtocolNodeRegistry, ProtocolNodeInfo

@runtime_checkable
class ProtocolNodeRegistry(Protocol):
    """
    Protocol for node discovery and registration services.

    Supports distributed node coordination with environment isolation,
    health monitoring, and comprehensive node lifecycle management
    following ONEX Messaging Design v0.3 patterns.

    Features:
        - Environment-based node isolation (dev, staging, prod)
        - Node group coordination for mini-mesh architectures
        - Consul-based service discovery integration
        - Health monitoring with heartbeat tracking
        - Real-time node change monitoring via watches
        - Gateway node management for groups
    """

    @property
    def environment(self) -> str:
        """Get current environment name (dev, staging, prod)."""
        ...

    @property
    def consul_endpoint(self) -> Optional[str]:
        """Get Consul endpoint configuration if available."""
        ...

    @property
    def config(self) -> Optional[ProtocolNodeRegistryConfig]:
        """Get registry configuration protocol."""
        ...

    async def register_node(
        self, node_info: ProtocolNodeInfo, ttl_seconds: int
    ) -> bool:
        """
        Register a node in the distributed registry.

        Args:
            node_info: Complete node information for registration
            ttl_seconds: Time-to-live for registration before renewal required

        Returns:
            True if registration successful

        Raises:
            RegistrationError: If node registration fails
            ValidationError: If node_info is invalid
        """
        ...

    async def unregister_node(self, node_id: str) -> bool:
        """
        Unregister a node from the registry.

        Args:
            node_id: Unique node identifier to remove

        Returns:
            True if unregistration successful

        Raises:
            RegistrationError: If unregistration fails
        """
        ...

    async def update_node_health(
        self,
        node_id: str,
        health_status: HealthStatus,
        metadata: dict[str, ContextValue],
    ) -> bool:
        """
        Update node health status with metadata.

        Args:
            node_id: Node identifier to update
            health_status: New health status (healthy, degraded, unhealthy, critical)
            metadata: Health status metadata (metrics, error details, etc.)

        Returns:
            True if update successful

        Raises:
            NodeNotFoundError: If node is not registered
            HealthUpdateError: If health update fails
        """
        ...

    async def heartbeat(self, node_id: str) -> bool:
        """
        Send heartbeat for a registered node to maintain registration.

        Args:
            node_id: Node identifier for heartbeat

        Returns:
            True if heartbeat accepted

        Raises:
            NodeNotFoundError: If node is not registered
            HeartbeatError: If heartbeat fails
        """
        ...

    async def discover_nodes(
        self,
        node_type: Optional[NodeType] = None,
        environment: Optional[str] = None,
        group: Optional[str] = None,
        health_filter: Optional[HealthStatus] = None,
    ) -> list[ProtocolNodeInfo]:
        """
        Discover nodes matching specified criteria.

        Args:
            node_type: Filter by node type (COMPUTE, ORCHESTRATOR, GATEWAY, etc.)
            environment: Filter by environment (default: current environment)
            group: Filter by node group for targeted discovery
            health_filter: Filter by health status (healthy, degraded, etc.)

        Returns:
            List of matching node information objects

        Raises:
            DiscoveryError: If node discovery fails
        """
        ...

    async def get_node(self, node_id: str) -> Optional[ProtocolNodeInfo]:
        """
        Get specific node information by ID.

        Args:
            node_id: Unique node identifier

        Returns:
            Node information if found, None otherwise

        Raises:
            RegistryError: If registry operation fails
        """
        ...

    async def get_nodes_by_group(self, group: str) -> list[ProtocolNodeInfo]:
        """
        Get all nodes in a specific node group.

        Args:
            group: Node group name for group-based operations

        Returns:
            List of nodes in the specified group

        Raises:
            RegistryError: If registry operation fails
        """
        ...

    async def get_gateway_for_group(self, group: str) -> Optional[ProtocolNodeInfo]:
        """
        Get the Group Gateway node for a node group.

        Group Gateways handle inter-group communication in mini-mesh architecture.

        Args:
            group: Node group name

        Returns:
            Gateway node info if available, None if no gateway registered

        Raises:
            RegistryError: If registry operation fails
        """
        ...

    async def watch_node_changes(
        self,
        callback: ProtocolNodeChangeCallback,
        node_type: Optional[NodeType] = None,
        group: Optional[str] = None,
    ) -> ProtocolWatchHandle:
        """
        Watch for real-time node registry changes.

        Args:
            callback: Function to call when nodes change (added, removed, health changed)
            node_type: Optional filter by node type
            group: Optional filter by node group

        Returns:
            Watch handle for cleanup and management

        Raises:
            WatchError: If watch setup fails
        """
        ...

    async def stop_watch(self, watch_handle: ProtocolWatchHandle) -> None:
        """
        Stop watching node changes and cleanup resources.

        Args:
            watch_handle: Handle returned by watch_node_changes

        Raises:
            WatchError: If watch cleanup fails
        """
        ...
```

### Workflow Reducer Protocol

```python
from omnibase_spi.protocols.core import ProtocolWorkflowReducer

@runtime_checkable
class ProtocolWorkflowReducer(Protocol):
    """
    Enhanced workflow reducer protocol with asynchronous capabilities.

    Supports both traditional synchronous state transitions and advanced
    workflow-based asynchronous orchestration with observable state changes,
    event emission, and monadic composition patterns.

    Features:
        - Immutable state management with pure reduction functions
        - Asynchronous workflow-based state transitions
        - Observable state changes via ProtocolNodeResult
        - Event sourcing support through event emission
        - Monadic composition with comprehensive error handling
        - Schema validation for states and actions
        - Integration with LlamaIndex workflow patterns
    """

    def initial_state(self) -> ProtocolState:
        """
        Return the initial state for this reducer.

        Returns:
            ProtocolState: Immutable initial state object
        """
        ...

    def dispatch(self, state: ProtocolState, action: ProtocolAction) -> ProtocolState:
        """
        Synchronous state transition for simple, fast operations.

        Pure function that takes current state and action, returns new state.
        Should be used for simple, synchronous state updates that don't
        require external I/O or complex orchestration.

        Args:
            state: Current immutable state
            action: Action object describing the state change

        Returns:
            ProtocolState: New immutable state after applying action

        Raises:
            ActionError: If action is invalid or cannot be processed
            StateError: If resulting state would be invalid
        """
        ...

    async def dispatch_async(
        self, state: ProtocolState, action: ProtocolAction
    ) -> ProtocolNodeResult:
        """
        Asynchronous workflow-based state transition.

        Enables complex state transitions involving multiple async operations,
        external service calls, error recovery, and event emission. Returns
        monadic result with comprehensive context and error handling.

        Args:
            state: Current immutable state
            action: Action object describing the complex state change

        Returns:
            ProtocolNodeResult: Monadic result containing new state, events,
                               context information, and error handling

        Raises:
            WorkflowError: If workflow execution fails
            AsyncActionError: If async action processing fails
        """
        ...

    def create_workflow(self) -> Optional[ProtocolWorkflow]:
        """
        Factory method for creating workflow instances for complex orchestration.

        Returns:
            Optional[ProtocolWorkflow]: Workflow instance for LlamaIndex integration,
                                       or None if using synchronous dispatch only

        Raises:
            WorkflowCreationError: If workflow cannot be created
        """
        ...

    def validate_state_transition(
        self, from_state: ProtocolState, action: ProtocolAction, to_state: ProtocolState
    ) -> bool:
        """
        Validate that a state transition is legal and consistent.

        Args:
            from_state: Source state before transition
            action: Action being applied
            to_state: Target state after transition

        Returns:
            bool: True if transition is valid, False otherwise
        """
        ...

    def get_state_schema(self) -> Optional[dict[str, Any]]:
        """
        Get JSON schema definition for this reducer's state structure.

        Returns:
            Optional[dict[str, Any]]: JSON schema for state validation,
                                    or None if schema not available
        """
        ...

    def get_action_schema(self) -> Optional[dict[str, Any]]:
        """
        Get JSON schema definition for actions this reducer handles.

        Returns:
            Optional[dict[str, Any]]: JSON schema for action validation,
                                    or None if schema not available
        """
        ...
```

### Node Configuration Protocol

```python
from omnibase_spi.protocols.core import (
    ProtocolNodeConfiguration,
    ProtocolNodeConfigurationProvider,
    ProtocolUtilsNodeConfiguration
)

@runtime_checkable
class ProtocolNodeConfiguration(Protocol):
    """
    Protocol for node configuration management.

    Provides comprehensive configuration handling with environment-specific
    overrides, validation, and dynamic reloading capabilities.

    Features:
        - Environment-specific configuration management
        - Configuration validation and schema checking
        - Dynamic configuration reloading
        - Secure secrets management
        - Configuration inheritance and overrides
        - Performance optimization through caching
    """

    def get_config_value(
        self, key: str, default: Optional[Any] = None
    ) -> Any:
        """
        Get configuration value by key with optional default.

        Args:
            key: Configuration key (supports dot notation: "database.host")
            default: Default value if key not found

        Returns:
            Configuration value or default

        Raises:
            ConfigurationError: If key is invalid or configuration is corrupted
        """
        ...

    def set_config_value(self, key: str, value: Any) -> bool:
        """
        Set configuration value (runtime override).

        Args:
            key: Configuration key to set
            value: Value to set (must be serializable)

        Returns:
            True if value was set successfully

        Raises:
            ConfigurationError: If key is invalid or value cannot be set
        """
        ...

    def get_environment_config(self, environment: str) -> dict[str, Any]:
        """
        Get configuration for specific environment.

        Args:
            environment: Environment name (dev, staging, prod, etc.)

        Returns:
            Environment-specific configuration dictionary

        Raises:
            EnvironmentError: If environment is not configured
        """
        ...

    def validate_configuration(self) -> bool:
        """
        Validate current configuration against schema.

        Returns:
            True if configuration is valid

        Raises:
            ValidationError: If configuration is invalid with details
        """
        ...

    def reload_configuration(self) -> bool:
        """
        Reload configuration from source.

        Returns:
            True if reload was successful

        Raises:
            ConfigurationError: If reload fails
        """
        ...

@runtime_checkable
class ProtocolNodeConfigurationProvider(Protocol):
    """Protocol for configuration provider services."""

    def create_configuration(self, config_path: str) -> ProtocolNodeConfiguration:
        """Create configuration instance from path."""
        ...

    def get_configuration_schema(self) -> dict[str, Any]:
        """Get configuration validation schema."""
        ...

@runtime_checkable
class ProtocolUtilsNodeConfiguration(Protocol):
    """Protocol for configuration utilities and helpers."""

    def merge_configurations(
        self, base_config: dict, override_config: dict
    ) -> dict[str, Any]:
        """Merge configuration dictionaries with override precedence."""
        ...

    def validate_config_schema(
        self, config: dict, schema: dict
    ) -> bool:
        """Validate configuration against JSON schema."""
        ...

    def interpolate_config_values(
        self, config: dict, context: dict[str, str]
    ) -> dict[str, Any]:
        """Interpolate configuration values with context variables."""
        ...
```

## Type Definitions

### Core System Types

```python
from omnibase_spi.protocols.types.core_types import (
    HealthStatus,
    NodeType,
    ContextValue,
    ProtocolState,
    ProtocolAction,
    ProtocolNodeResult,
    ProtocolDateTime,
    ProtocolSemVer,
    ProtocolNodeMetadata
)

# Health status enumeration
HealthStatus = Literal["healthy", "degraded", "unhealthy", "critical", "unknown"]

# Node type enumeration  
NodeType = Literal[
    "COMPUTE",
    "ORCHESTRATOR",
    "GATEWAY",
    "STORAGE",
    "MONITOR",
    "COORDINATOR",
    "WORKER",
    "SCHEDULER"
]

# Context value types
ContextValue = str | int | float | bool | list[str] | dict[str, Any]

# Core workflow types
ProtocolState = dict[str, Any]
ProtocolAction = dict[str, Any]

@runtime_checkable
class ProtocolNodeResult(Protocol):
    """Protocol for monadic node operation results."""

    value: Any
    is_success: bool
    is_failure: bool
    events: list[dict[str, Any]]
    context: dict[str, Any]
    error: Optional[dict[str, Any]]

@runtime_checkable
class ProtocolNodeInfo(Protocol):
    """Protocol for comprehensive node information."""

    node_id: str
    node_type: NodeType
    node_name: str
    environment: str
    group: str
    version: ProtocolSemVer
    health_status: HealthStatus
    endpoint: str
    metadata: dict[str, ContextValue]
    registered_at: ProtocolDateTime
    last_heartbeat: ProtocolDateTime

@runtime_checkable
class ProtocolCacheStatistics(Protocol):
    """Protocol for cache performance statistics."""

    hit_count: int
    miss_count: int
    hit_ratio: float
    total_operations: int
    memory_usage_bytes: int
    eviction_count: int
    average_operation_time: float
    cache_size: int
```

### Configuration Types

```python
@runtime_checkable
class ProtocolNodeRegistryConfig(Protocol):
    """Protocol for node registry configuration."""

    consul_host: str
    consul_port: int
    consul_token: Optional[str]
    health_check_interval: int
    retry_attempts: int

@runtime_checkable
class ProtocolConfigurationError(Protocol):
    """Protocol for configuration error objects."""

    error_type: str
    message: str
    key: Optional[str]
    context: dict[str, Any]

# Callback and handle protocols
@runtime_checkable
class ProtocolNodeChangeCallback(Protocol):
    """Protocol for node change callback functions."""

    def __call__(self, node_info: ProtocolNodeInfo, change_type: str) -> None:
        """Handle node registry changes."""
        ...

@runtime_checkable
class ProtocolWatchHandle(Protocol):
    """Protocol for watch handle objects."""

    watch_id: str
    is_active: bool
```

## Usage Patterns

### Basic Cache Service Usage

```python
from omnibase_spi.protocols.core import ProtocolCacheService

class RedisCacheService:
    """Example Redis cache service implementation."""

    def __init__(self, redis_client, default_ttl: int = 3600):
        self.redis_client = redis_client
        self.default_ttl = default_ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            data = await self.redis_client.get(key)
            if data is not None:
                self.stats["hits"] += 1
                return json.loads(data)
            else:
                self.stats["misses"] += 1
                return None
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            self.stats["misses"] += 1
            return None

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        try:
            ttl = ttl_seconds or self.default_ttl
            data = json.dumps(value)
            result = await self.redis_client.setex(key, ttl, data)
            self.stats["sets"] += 1
            return bool(result)
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        try:
            result = await self.redis_client.delete(key)
            self.stats["deletes"] += 1
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False

    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries by pattern."""
        try:
            if pattern:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    result = await self.redis_client.delete(*keys)
                    return result
                return 0
            else:
                # Clear all keys (use with caution)
                result = await self.redis_client.flushdb()
                return 1 if result else 0
        except Exception as e:
            logger.error(f"Cache clear failed for pattern {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache exists check failed for key {key}: {e}")
            return False

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_ops = self.stats["hits"] + self.stats["misses"]
        hit_ratio = self.stats["hits"] / total_ops if total_ops > 0 else 0

        return {
            "hit_count": self.stats["hits"],
            "miss_count": self.stats["misses"],
            "hit_ratio": hit_ratio,
            "total_operations": total_ops,
            "cache_size": -1,  # Would need separate Redis call
            "memory_usage_bytes": -1,  # Would need Redis info command
            "eviction_count": 0,
            "average_operation_time": 0.001  # Placeholder
        }

# Usage example
async def use_cache_service():
    """Example using cache service."""

    # Create cache service (Redis client would be injected)
    cache: ProtocolCacheService[dict] = RedisCacheService(redis_client)

    # Cache user data
    user_data = {
        "user_id": "12345",
        "name": "John Doe",
        "email": "john@example.com",
        "permissions": ["read", "write"]
    }

    # Set with TTL
    success = await cache.set("user:12345", user_data, ttl_seconds=3600)
    print(f"Cache set successful: {success}")

    # Get from cache
    cached_user = await cache.get("user:12345")
    print(f"Retrieved user: {cached_user}")

    # Check existence
    exists = await cache.exists("user:12345")
    print(f"User exists in cache: {exists}")

    # Clear user-related cache
    cleared_count = await cache.clear("user:*")
    print(f"Cleared {cleared_count} user cache entries")

    # Get cache statistics
    stats = cache.get_stats()
    print(f"Cache hit ratio: {stats['hit_ratio']:.2%}")
```

### Node Registry Operations

```python
from omnibase_spi.protocols.core import ProtocolNodeRegistry

class ConsulNodeRegistry:
    """Example Consul-based node registry implementation."""

    def __init__(self, consul_client, environment: str = "dev"):
        self.consul = consul_client
        self.environment = environment
        self.watches = {}

    @property
    def environment(self) -> str:
        return self._environment

    @property
    def consul_endpoint(self) -> Optional[str]:
        return f"{self.consul.host}:{self.consul.port}"

    async def register_node(
        self, node_info: ProtocolNodeInfo, ttl_seconds: int
    ) -> bool:
        """Register node with Consul."""
        try:
            service_name = f"{self.environment}-{node_info.group}-{node_info.node_type}"
            service_id = f"{node_info.node_id}-{self.environment}"

            # Parse endpoint
            host, port = node_info.endpoint.split(":")

            # Register service with health check
            result = await self.consul.agent.service.register(
                name=service_name,
                service_id=service_id,
                address=host,
                port=int(port),
                tags=[node_info.group, str(node_info.version)],
                meta=dict(node_info.metadata),
                check={
                    "ttl": f"{ttl_seconds}s",
                    "status": "passing"
                }
            )

            return bool(result)
        except Exception as e:
            logger.error(f"Node registration failed: {e}")
            return False

    async def discover_nodes(
        self,
        node_type: Optional[NodeType] = None,
        environment: Optional[str] = None,
        group: Optional[str] = None,
        health_filter: Optional[HealthStatus] = None,
    ) -> list[ProtocolNodeInfo]:
        """Discover nodes from Consul catalog."""

        try:
            env = environment or self.environment
            service_filter = f"{env}-"

            if group:
                service_filter += f"{group}-"
            if node_type:
                service_filter += str(node_type)

            # Get services from Consul
            services = await self.consul.catalog.services()
            matching_nodes = []

            for service_name, tags in services.items():
                if service_name.startswith(service_filter):
                    # Get service details
                    service_nodes = await self.consul.catalog.service(service_name)

                    for node in service_nodes:
                        node_info = self._consul_node_to_protocol_node(node)

                        # Apply health filter
                        if health_filter and node_info.health_status != health_filter:
                            continue

                        matching_nodes.append(node_info)

            return matching_nodes

        except Exception as e:
            logger.error(f"Node discovery failed: {e}")
            return []

    async def heartbeat(self, node_id: str) -> bool:
        """Send heartbeat to maintain registration."""
        try:
            service_id = f"{node_id}-{self.environment}"
            result = await self.consul.agent.check.ttl_pass(f"service:{service_id}")
            return bool(result)
        except Exception as e:
            logger.error(f"Heartbeat failed for {node_id}: {e}")
            return False

    async def watch_node_changes(
        self,
        callback: ProtocolNodeChangeCallback,
        node_type: Optional[NodeType] = None,
        group: Optional[str] = None,
    ) -> ProtocolWatchHandle:
        """Watch for node changes via Consul watches."""

        watch_id = f"watch_{len(self.watches)}_{int(time.time())}"

        # Create watch configuration
        watch_config = {
            "type": "services",
            "prefix": f"{self.environment}-",
            "callback": callback
        }

        if group:
            watch_config["prefix"] += f"{group}-"
        if node_type:
            watch_config["prefix"] += str(node_type)

        # Start watch (implementation would depend on Consul client)
        watch_handle = ConsulWatchHandle(watch_id, True)
        self.watches[watch_id] = watch_config

        return watch_handle

    def _consul_node_to_protocol_node(self, consul_node: dict) -> ProtocolNodeInfo:
        """Convert Consul node data to protocol node info."""

        # Extract node information from Consul format
        node_id = consul_node["ServiceID"].split("-")[0]
        node_type = consul_node["ServiceName"].split("-")[-1]
        group = consul_node["ServiceTags"][0] if consul_node["ServiceTags"] else "default"

        return ProtocolNodeInfo(
            node_id=node_id,
            node_type=node_type,
            node_name=consul_node["ServiceName"],
            environment=self.environment,
            group=group,
            version=ProtocolSemVer(1, 0, 0),  # Parse from tags
            health_status="healthy",  # Map from Consul health
            endpoint=f"{consul_node['ServiceAddress']}:{consul_node['ServicePort']}",
            metadata=consul_node.get("ServiceMeta", {}),
            registered_at=datetime.utcnow().isoformat(),
            last_heartbeat=datetime.utcnow().isoformat()
        )

class ConsulWatchHandle:
    """Watch handle for Consul service watches."""

    def __init__(self, watch_id: str, is_active: bool):
        self.watch_id = watch_id
        self.is_active = is_active

# Usage example
async def use_node_registry():
    """Example using node registry."""

    registry: ProtocolNodeRegistry = ConsulNodeRegistry(consul_client, "prod")

    # Register current node
    node_info = ProtocolNodeInfo(
        node_id="worker-001",
        node_type="COMPUTE",
        node_name="Data Processing Worker",
        environment="prod",
        group="analytics",
        version=ProtocolSemVer(1, 2, 3),
        health_status="healthy",
        endpoint="10.0.1.15:8080",
        metadata={
            "cpu_cores": 8,
            "memory_gb": 32,
            "gpu_available": True,
            "capabilities": ["tensorflow", "pytorch"]
        },
        registered_at=datetime.utcnow().isoformat(),
        last_heartbeat=datetime.utcnow().isoformat()
    )

    # Register node with 60-second TTL
    success = await registry.register_node(node_info, ttl_seconds=60)
    print(f"Node registration: {'SUCCESS' if success else 'FAILED'}")

    # Discover other compute nodes in same group
    compute_nodes = await registry.discover_nodes(
        node_type="COMPUTE",
        group="analytics",
        health_filter="healthy"
    )

    print(f"Found {len(compute_nodes)} healthy compute nodes:")
    for node in compute_nodes:
        print(f"  - {node.node_name} at {node.endpoint}")

    # Set up node change monitoring
    async def on_node_change(node: ProtocolNodeInfo, change_type: str):
        print(f"Node change: {node.node_name} -> {change_type}")

        if change_type == "node_failed":
            # Implement failover logic
            await handle_node_failure(node)
        elif change_type == "node_added":
            # Update load balancing
            await update_load_balancer(node)

    watch_handle = await registry.watch_node_changes(
        callback=on_node_change,
        node_type="COMPUTE",
        group="analytics"
    )

    # Periodic heartbeat loop
    async def heartbeat_loop():
        while True:
            success = await registry.heartbeat(node_info.node_id)
            if not success:
                logger.warning("Heartbeat failed - may need to re-register")
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds

    # Start heartbeat task
    heartbeat_task = asyncio.create_task(heartbeat_loop())

    # Simulate running for some time
    await asyncio.sleep(300)  # Run for 5 minutes

    # Cleanup
    await registry.stop_watch(watch_handle)
    heartbeat_task.cancel()
    await registry.unregister_node(node_info.node_id)
```

### Workflow Reducer Implementation

```python
from omnibase_spi.protocols.core import ProtocolWorkflowReducer

class UserWorkflowReducer:
    """Example workflow reducer for user management."""

    def __init__(self):
        self.workflows = {}

    def initial_state(self) -> ProtocolState:
        """Return initial user management state."""
        return {
            "users": {},
            "active_sessions": {},
            "total_users": 0,
            "last_activity": None,
            "system_status": "initialized"
        }

    def dispatch(self, state: ProtocolState, action: ProtocolAction) -> ProtocolState:
        """Handle synchronous state transitions."""

        action_type = action.get("type")

        if action_type == "INCREMENT_SESSION_COUNT":
            return {
                **state,
                "active_sessions": {
                    **state["active_sessions"],
                    "count": state["active_sessions"].get("count", 0) + 1
                }
            }

        elif action_type == "SET_SYSTEM_STATUS":
            return {
                **state,
                "system_status": action["payload"]["status"],
                "last_activity": action["payload"]["timestamp"]
            }

        elif action_type == "ADD_USER_QUICK":
            user_id = action["payload"]["user_id"]
            user_data = action["payload"]["user_data"]

            return {
                **state,
                "users": {
                    **state["users"],
                    user_id: user_data
                },
                "total_users": state["total_users"] + 1,
                "last_activity": datetime.utcnow().isoformat()
            }

        # Return unchanged state for unknown actions
        return state

    async def dispatch_async(
        self, state: ProtocolState, action: ProtocolAction
    ) -> ProtocolNodeResult:
        """Handle asynchronous workflow-based transitions."""

        action_type = action.get("type")

        if action_type == "CREATE_USER_WORKFLOW":
            return await self._handle_user_creation_workflow(state, action)

        elif action_type == "DELETE_USER_WORKFLOW":
            return await self._handle_user_deletion_workflow(state, action)

        elif action_type == "UPDATE_USER_PERMISSIONS":
            return await self._handle_permission_update_workflow(state, action)

        else:
            # Unknown async action
            return ProtocolNodeResult(
                value=state,
                is_success=False,
                is_failure=True,
                events=[],
                context={"action_type": action_type},
                error={
                    "type": "unknown_async_action",
                    "message": f"Unknown async action type: {action_type}"
                }
            )

    async def _handle_user_creation_workflow(
        self, state: ProtocolState, action: ProtocolAction
    ) -> ProtocolNodeResult:
        """Handle complex user creation workflow."""

        try:
            user_data = action["payload"]["user_data"]
            events = []

            # Step 1: Validate user data
            validation_result = await self._validate_user_data(user_data)
            if not validation_result["valid"]:
                return ProtocolNodeResult(
                    value=state,
                    is_success=False,
                    is_failure=True,
                    events=[],
                    context={"step": "validation"},
                    error={
                        "type": "validation_failed",
                        "message": validation_result["error"],
                        "retryable": False
                    }
                )

            events.append({
                "type": "user_data_validated",
                "user_email": user_data["email"],
                "timestamp": datetime.utcnow().isoformat()
            })

            # Step 2: Create user in database
            user_id = await self._create_user_in_database(user_data)
            events.append({
                "type": "user_created_in_database",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Step 3: Send welcome email
            await self._send_welcome_email(user_id, user_data["email"])
            events.append({
                "type": "welcome_email_sent",
                "user_id": user_id,
                "email": user_data["email"],
                "timestamp": datetime.utcnow().isoformat()
            })

            # Step 4: Initialize user permissions
            await self._initialize_user_permissions(user_id, user_data.get("role", "user"))
            events.append({
                "type": "permissions_initialized",
                "user_id": user_id,
                "role": user_data.get("role", "user"),
                "timestamp": datetime.utcnow().isoformat()
            })

            # Update state with new user
            new_state = {
                **state,
                "users": {
                    **state["users"],
                    user_id: {
                        **user_data,
                        "user_id": user_id,
                        "created_at": datetime.utcnow().isoformat(),
                        "status": "active"
                    }
                },
                "total_users": state["total_users"] + 1,
                "last_activity": datetime.utcnow().isoformat()
            }

            return ProtocolNodeResult(
                value=new_state,
                is_success=True,
                is_failure=False,
                events=events,
                context={
                    "workflow_type": "user_creation",
                    "user_id": user_id,
                    "steps_completed": 4
                },
                error=None
            )

        except Exception as e:
            # Workflow failed - return error result
            return ProtocolNodeResult(
                value=state,
                is_success=False,
                is_failure=True,
                events=[{
                    "type": "workflow_failed",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }],
                context={
                    "workflow_type": "user_creation",
                    "failure_point": "unknown"
                },
                error={
                    "type": "workflow_exception",
                    "message": str(e),
                    "retryable": True
                }
            )

    async def _validate_user_data(self, user_data: dict) -> dict:
        """Validate user data."""
        # Simulate validation
        await asyncio.sleep(0.1)

        required_fields = ["email", "name", "password"]
        for field in required_fields:
            if field not in user_data:
                return {"valid": False, "error": f"Missing required field: {field}"}

        # Email validation
        if "@" not in user_data["email"]:
            return {"valid": False, "error": "Invalid email format"}

        return {"valid": True}

    async def _create_user_in_database(self, user_data: dict) -> str:
        """Create user in database."""
        # Simulate database operation
        await asyncio.sleep(0.2)
        user_id = str(uuid.uuid4())
        return user_id

    async def _send_welcome_email(self, user_id: str, email: str) -> None:
        """Send welcome email."""
        # Simulate email sending
        await asyncio.sleep(0.3)
        logger.info(f"Welcome email sent to {email} for user {user_id}")

    async def _initialize_user_permissions(self, user_id: str, role: str) -> None:
        """Initialize user permissions."""
        # Simulate permission setup
        await asyncio.sleep(0.1)
        logger.info(f"Permissions initialized for user {user_id} with role {role}")

    def validate_state_transition(
        self, from_state: ProtocolState, action: ProtocolAction, to_state: ProtocolState
    ) -> bool:
        """Validate state transition logic."""

        # Check that user count is monotonic for user additions
        if action.get("type") in ["ADD_USER_QUICK", "CREATE_USER_WORKFLOW"]:
            return to_state["total_users"] >= from_state["total_users"]

        # Check that timestamps move forward
        if "last_activity" in to_state and "last_activity" in from_state:
            if to_state["last_activity"] and from_state["last_activity"]:
                return to_state["last_activity"] >= from_state["last_activity"]

        return True

    def get_state_schema(self) -> Optional[dict[str, Any]]:
        """Get state schema definition."""
        return {
            "type": "object",
            "properties": {
                "users": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "email": {"type": "string"},
                            "name": {"type": "string"},
                            "status": {"type": "string"},
                            "created_at": {"type": "string"}
                        },
                        "required": ["user_id", "email", "name"]
                    }
                },
                "active_sessions": {"type": "object"},
                "total_users": {"type": "integer", "minimum": 0},
                "last_activity": {"type": ["string", "null"]},
                "system_status": {"type": "string"}
            },
            "required": ["users", "active_sessions", "total_users", "system_status"]
        }

    def get_action_schema(self) -> Optional[dict[str, Any]]:
        """Get action schema definition."""
        return {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": [
                        "INCREMENT_SESSION_COUNT",
                        "SET_SYSTEM_STATUS",
                        "ADD_USER_QUICK",
                        "CREATE_USER_WORKFLOW",
                        "DELETE_USER_WORKFLOW",
                        "UPDATE_USER_PERMISSIONS"
                    ]
                },
                "payload": {"type": "object"}
            },
            "required": ["type"]
        }

# Usage example
async def use_workflow_reducer():
    """Example using workflow reducer."""

    reducer: ProtocolWorkflowReducer = UserWorkflowReducer()

    # Get initial state
    state = reducer.initial_state()
    print(f"Initial state: {state}")

    # Synchronous action
    sync_action = {
        "type": "INCREMENT_SESSION_COUNT",
        "payload": {}
    }

    new_state = reducer.dispatch(state, sync_action)
    print(f"After sync action: {new_state['active_sessions']}")

    # Asynchronous workflow action
    async_action = {
        "type": "CREATE_USER_WORKFLOW",
        "payload": {
            "user_data": {
                "email": "alice@example.com",
                "name": "Alice Smith",
                "password": "secure_password",
                "role": "admin"
            }
        }
    }

    result = await reducer.dispatch_async(new_state, async_action)

    if result.is_success:
        print(f"User creation successful!")
        print(f"Events generated: {len(result.events)}")
        for event in result.events:
            print(f"  - {event['type']}: {event.get('timestamp', 'no timestamp')}")

        final_state = result.value
        print(f"Total users: {final_state['total_users']}")
    else:
        print(f"User creation failed: {result.error}")
```

## Advanced Features

### Multi-Environment Configuration

```python
import os
from typing import Dict, Any
import yaml

class EnvironmentAwareConfiguration:
    """Configuration with environment-specific overrides."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.current_env = os.getenv("ONEX_ENVIRONMENT", "dev")
        self.base_config = {}
        self.env_config = {}
        self.runtime_overrides = {}
        self.load_configuration()

    def load_configuration(self) -> None:
        """Load base and environment-specific configurations."""

        # Load base configuration
        base_config_path = self.config_dir / "base.yaml"
        if base_config_path.exists():
            with open(base_config_path) as f:
                self.base_config = yaml.safe_load(f) or {}

        # Load environment-specific configuration
        env_config_path = self.config_dir / f"{self.current_env}.yaml"
        if env_config_path.exists():
            with open(env_config_path) as f:
                self.env_config = yaml.safe_load(f) or {}

    def get_config_value(self, key: str, default: Optional[Any] = None) -> Any:
        """Get configuration value with environment override precedence."""

        # Split key for nested access
        keys = key.split('.')

        # Check runtime overrides first
        value = self._get_nested_value(self.runtime_overrides, keys, None)
        if value is not None:
            return value

        # Check environment-specific config
        value = self._get_nested_value(self.env_config, keys, None)
        if value is not None:
            return value

        # Check base config
        value = self._get_nested_value(self.base_config, keys, None)
        if value is not None:
            return value

        # Return default
        return default

    def set_config_value(self, key: str, value: Any) -> bool:
        """Set runtime configuration override."""

        try:
            keys = key.split('.')
            self._set_nested_value(self.runtime_overrides, keys, value)
            return True
        except Exception as e:
            logger.error(f"Failed to set config value {key}: {e}")
            return False

    def get_environment_config(self, environment: str) -> dict[str, Any]:
        """Get configuration for specific environment."""

        env_config_path = self.config_dir / f"{environment}.yaml"
        if env_config_path.exists():
            with open(env_config_path) as f:
                return yaml.safe_load(f) or {}
        else:
            raise EnvironmentError(f"Environment {environment} not configured")

    def validate_configuration(self) -> bool:
        """Validate current configuration."""

        # Basic validation - check required keys
        required_keys = [
            "database.host",
            "database.port",
            "redis.host",
            "logging.level"
        ]

        for key in required_keys:
            value = self.get_config_value(key)
            if value is None:
                logger.error(f"Required configuration key missing: {key}")
                return False

        # Type validation
        if not isinstance(self.get_config_value("database.port"), int):
            logger.error("database.port must be an integer")
            return False

        return True

    def reload_configuration(self) -> bool:
        """Reload configuration from files."""
        try:
            self.runtime_overrides.clear()
            self.load_configuration()
            return self.validate_configuration()
        except Exception as e:
            logger.error(f"Configuration reload failed: {e}")
            return False

    def _get_nested_value(self, config: dict, keys: list, default: Any) -> Any:
        """Get value from nested dictionary."""
        current = config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def _set_nested_value(self, config: dict, keys: list, value: Any) -> None:
        """Set value in nested dictionary."""
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

# Usage
async def use_environment_configuration():
    """Example using environment-aware configuration."""

    config = EnvironmentAwareConfiguration("config/")

    # Get database configuration
    db_host = config.get_config_value("database.host", "localhost")
    db_port = config.get_config_value("database.port", 5432)

    print(f"Database: {db_host}:{db_port}")

    # Runtime override
    config.set_config_value("database.max_connections", 50)
    max_conn = config.get_config_value("database.max_connections")
    print(f"Max connections: {max_conn}")

    # Environment-specific config
    try:
        prod_config = config.get_environment_config("prod")
        print(f"Production database: {prod_config.get('database', {})}")
    except EnvironmentError as e:
        print(f"Production config not available: {e}")

    # Validate configuration
    if config.validate_configuration():
        print("Configuration is valid")
    else:
        print("Configuration validation failed")
```

### Distributed Cache Coordination

```python
import asyncio
from typing import List
import hashlib

class DistributedCacheCoordinator:
    """Coordinator for multiple cache instances."""

    def __init__(self, cache_services: List[ProtocolCacheService]):
        self.cache_services = cache_services
        self.hash_ring = self._build_hash_ring()

    def _build_hash_ring(self) -> dict:
        """Build consistent hash ring for cache distribution."""
        ring = {}
        for i, cache_service in enumerate(self.cache_services):
            # Create multiple virtual nodes for better distribution
            for j in range(100):  # 100 virtual nodes per cache
                node_key = f"cache_{i}_vnode_{j}"
                hash_value = int(hashlib.md5(node_key.encode()).hexdigest(), 16)
                ring[hash_value] = i

        return dict(sorted(ring.items()))

    def _get_cache_for_key(self, key: str) -> ProtocolCacheService:
        """Get cache service for key using consistent hashing."""
        key_hash = int(hashlib.md5(key.encode()).hexdigest(), 16)

        # Find the first cache node with hash >= key_hash
        for hash_value, cache_index in self.hash_ring.items():
            if hash_value >= key_hash:
                return self.cache_services[cache_index]

        # Wrap around to first cache if no match
        first_cache_index = next(iter(self.hash_ring.values()))
        return self.cache_services[first_cache_index]

    async def get(self, key: str) -> Optional[Any]:
        """Get value using consistent hashing."""
        cache_service = self._get_cache_for_key(key)
        return await cache_service.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value using consistent hashing."""
        cache_service = self._get_cache_for_key(key)
        return await cache_service.set(key, value, ttl_seconds)

    async def delete(self, key: str) -> bool:
        """Delete value using consistent hashing."""
        cache_service = self._get_cache_for_key(key)
        return await cache_service.delete(key)

    async def clear_all(self, pattern: Optional[str] = None) -> int:
        """Clear pattern from all cache services."""
        tasks = [
            cache_service.clear(pattern)
            for cache_service in self.cache_services
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_cleared = sum(r for r in results if isinstance(r, int))

        return total_cleared

    async def get_aggregate_stats(self) -> dict:
        """Get aggregated statistics from all cache services."""

        tasks = [
            cache_service.get_stats()
            for cache_service in self.cache_services
        ]

        all_stats = await asyncio.gather(*tasks, return_exceptions=True)
        valid_stats = [s for s in all_stats if not isinstance(s, Exception)]

        if not valid_stats:
            return {"error": "No cache statistics available"}

        # Aggregate statistics
        total_hits = sum(s.get("hit_count", 0) for s in valid_stats)
        total_misses = sum(s.get("miss_count", 0) for s in valid_stats)
        total_ops = total_hits + total_misses

        return {
            "cache_count": len(valid_stats),
            "total_hit_count": total_hits,
            "total_miss_count": total_misses,
            "aggregate_hit_ratio": total_hits / total_ops if total_ops > 0 else 0,
            "total_operations": total_ops,
            "average_memory_usage": sum(s.get("memory_usage_bytes", 0) for s in valid_stats) / len(valid_stats),
            "individual_stats": valid_stats
        }

# Usage
async def use_distributed_cache():
    """Example using distributed cache coordination."""

    # Create multiple cache services
    cache_services = [
        RedisCacheService(redis_client_1),
        RedisCacheService(redis_client_2),
        RedisCacheService(redis_client_3)
    ]

    coordinator = DistributedCacheCoordinator(cache_services)

    # Test distributed operations
    test_data = {
        "user:1": {"name": "Alice", "role": "admin"},
        "user:2": {"name": "Bob", "role": "user"},
        "session:abc": {"user_id": "1", "expires": "2024-12-31"},
        "config:app": {"theme": "dark", "notifications": True}
    }

    # Set values (distributed across caches)
    for key, value in test_data.items():
        success = await coordinator.set(key, value, ttl_seconds=3600)
        print(f"Set {key}: {'SUCCESS' if success else 'FAILED'}")

    # Get values back
    for key in test_data.keys():
        value = await coordinator.get(key)
        print(f"Get {key}: {value}")

    # Get aggregate statistics
    stats = await coordinator.get_aggregate_stats()
    print(f"Distributed cache stats:")
    print(f"  Total operations: {stats['total_operations']}")
    print(f"  Hit ratio: {stats['aggregate_hit_ratio']:.2%}")
    print(f"  Cache instances: {stats['cache_count']}")
```

## Integration with Other Domains

### Event Bus Integration

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBus

class EventDrivenNodeRegistry:
    """Node registry that publishes events for node changes."""

    def __init__(self, base_registry: ProtocolNodeRegistry, event_bus: ProtocolEventBus):
        self.base_registry = base_registry
        self.event_bus = event_bus

    async def register_node(
        self, node_info: ProtocolNodeInfo, ttl_seconds: int
    ) -> bool:
        """Register node and publish event."""

        success = await self.base_registry.register_node(node_info, ttl_seconds)

        if success:
            # Publish node registration event
            await self.event_bus.publish_event(
                EventMessage(
                    event_id=str(uuid4()),
                    event_type="node.registered",
                    payload={
                        "node_id": node_info.node_id,
                        "node_type": node_info.node_type,
                        "node_name": node_info.node_name,
                        "environment": node_info.environment,
                        "group": node_info.group,
                        "endpoint": node_info.endpoint,
                        "ttl_seconds": ttl_seconds
                    },
                    metadata=EventMetadata(
                        source="node_registry",
                        correlation_id=str(uuid4())
                    ),
                    timestamp=datetime.utcnow().isoformat()
                )
            )

        return success

    async def update_node_health(
        self,
        node_id: str,
        health_status: HealthStatus,
        metadata: dict[str, ContextValue],
    ) -> bool:
        """Update health and publish event."""

        # Get current node info for comparison
        current_node = await self.base_registry.get_node(node_id)
        previous_health = current_node.health_status if current_node else "unknown"

        success = await self.base_registry.update_node_health(node_id, health_status, metadata)

        if success and health_status != previous_health:
            # Publish health change event
            await self.event_bus.publish_event(
                EventMessage(
                    event_id=str(uuid4()),
                    event_type="node.health_changed",
                    payload={
                        "node_id": node_id,
                        "previous_health": previous_health,
                        "current_health": health_status,
                        "metadata": metadata
                    },
                    metadata=EventMetadata(source="node_registry"),
                    timestamp=datetime.utcnow().isoformat()
                )
            )

        return success
```

### MCP Tool Integration

```python
from omnibase_spi.protocols.mcp import ProtocolMCPRegistry

class MCPAwareCacheService:
    """Cache service that can be controlled via MCP tools."""

    def __init__(self, base_cache: ProtocolCacheService, mcp_registry: ProtocolMCPRegistry):
        self.base_cache = base_cache
        self.mcp_registry = mcp_registry
        self.register_mcp_tools()

    def register_mcp_tools(self) -> None:
        """Register cache management tools with MCP."""

        # Cache statistics tool
        stats_tool = MCPToolDefinition(
            name="cache_stats",
            tool_type="query",
            parameters_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            description="Get cache performance statistics"
        )

        # Cache clear tool
        clear_tool = MCPToolDefinition(
            name="cache_clear",
            tool_type="action",
            parameters_schema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Pattern to match for clearing"}
                },
                "required": []
            },
            description="Clear cache entries by pattern"
        )

        # Register tools
        self.mcp_registry.register_tool(stats_tool, self._handle_stats_tool)
        self.mcp_registry.register_tool(clear_tool, self._handle_clear_tool)

    async def _handle_stats_tool(self, parameters: dict) -> dict:
        """Handle cache statistics tool request."""
        stats = self.base_cache.get_stats()
        return {
            "success": True,
            "data": stats,
            "message": "Cache statistics retrieved successfully"
        }

    async def _handle_clear_tool(self, parameters: dict) -> dict:
        """Handle cache clear tool request."""
        pattern = parameters.get("pattern")
        cleared_count = await self.base_cache.clear(pattern)

        return {
            "success": True,
            "data": {"cleared_count": cleared_count},
            "message": f"Cleared {cleared_count} cache entries"
        }

    # Delegate all other cache operations to base cache
    async def get(self, key: str) -> Optional[Any]:
        return await self.base_cache.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        return await self.base_cache.set(key, value, ttl_seconds)

    # ... other cache methods
```

## Testing Strategies

### Core Protocol Testing

```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestCacheServiceProtocol:
    """Test suite for cache service protocol compliance."""

    @pytest.fixture
    def mock_cache_service(self):
        """Create mock cache service for testing."""

        cache = Mock()
        cache.get = AsyncMock()
        cache.set = AsyncMock()
        cache.delete = AsyncMock()
        cache.clear = AsyncMock()
        cache.exists = AsyncMock()
        cache.get_stats = Mock()

        return cache

    async def test_cache_get_operation(self, mock_cache_service):
        """Test cache get operation."""

        # Setup
        mock_cache_service.get.return_value = {"user_id": "123", "name": "Alice"}

        # Test
        result = await mock_cache_service.get("user:123")

        # Verify
        assert result is not None
        assert result["user_id"] == "123"
        mock_cache_service.get.assert_called_once_with("user:123")

    async def test_cache_set_operation(self, mock_cache_service):
        """Test cache set operation."""

        # Setup
        mock_cache_service.set.return_value = True

        # Test
        success = await mock_cache_service.set("user:123", {"name": "Alice"}, ttl_seconds=3600)

        # Verify
        assert success is True
        mock_cache_service.set.assert_called_once_with("user:123", {"name": "Alice"}, ttl_seconds=3600)

    async def test_cache_statistics(self, mock_cache_service):
        """Test cache statistics retrieval."""

        # Setup
        expected_stats = {
            "hit_count": 100,
            "miss_count": 20,
            "hit_ratio": 0.83,
            "total_operations": 120
        }
        mock_cache_service.get_stats.return_value = expected_stats

        # Test
        stats = mock_cache_service.get_stats()

        # Verify
        assert stats["hit_ratio"] == 0.83
        assert stats["total_operations"] == 120

class TestNodeRegistryProtocol:
    """Test suite for node registry protocol compliance."""

    @pytest.fixture
    def mock_node_registry(self):
        """Create mock node registry for testing."""

        registry = Mock()
        registry.environment = "test"
        registry.consul_endpoint = "localhost:8500"
        registry.register_node = AsyncMock()
        registry.discover_nodes = AsyncMock()
        registry.heartbeat = AsyncMock()
        registry.watch_node_changes = AsyncMock()

        return registry

    @pytest.fixture
    def sample_node_info(self):
        """Create sample node info for testing."""

        return ProtocolNodeInfo(
            node_id="test-node-001",
            node_type="COMPUTE",
            node_name="Test Compute Node",
            environment="test",
            group="test-group",
            version=ProtocolSemVer(1, 0, 0),
            health_status="healthy",
            endpoint="localhost:8080",
            metadata={"cpu_cores": 4, "memory_gb": 8},
            registered_at=datetime.utcnow().isoformat(),
            last_heartbeat=datetime.utcnow().isoformat()
        )

    async def test_node_registration(self, mock_node_registry, sample_node_info):
        """Test node registration."""

        # Setup
        mock_node_registry.register_node.return_value = True

        # Test
        success = await mock_node_registry.register_node(sample_node_info, 60)

        # Verify
        assert success is True
        mock_node_registry.register_node.assert_called_once_with(sample_node_info, 60)

    async def test_node_discovery(self, mock_node_registry, sample_node_info):
        """Test node discovery."""

        # Setup
        mock_node_registry.discover_nodes.return_value = [sample_node_info]

        # Test
        nodes = await mock_node_registry.discover_nodes(
            node_type="COMPUTE",
            environment="test",
            health_filter="healthy"
        )

        # Verify
        assert len(nodes) == 1
        assert nodes[0].node_id == "test-node-001"
        mock_node_registry.discover_nodes.assert_called_once_with(
            node_type="COMPUTE",
            environment="test",
            group=None,
            health_filter="healthy"
        )

class TestWorkflowReducerProtocol:
    """Test suite for workflow reducer protocol compliance."""

    @pytest.fixture
    def mock_workflow_reducer(self):
        """Create mock workflow reducer for testing."""

        reducer = Mock()
        reducer.initial_state = Mock()
        reducer.dispatch = Mock()
        reducer.dispatch_async = AsyncMock()
        reducer.validate_state_transition = Mock()

        return reducer

    def test_initial_state(self, mock_workflow_reducer):
        """Test initial state generation."""

        # Setup
        expected_state = {"counter": 0, "status": "initialized"}
        mock_workflow_reducer.initial_state.return_value = expected_state

        # Test
        state = mock_workflow_reducer.initial_state()

        # Verify
        assert state["counter"] == 0
        assert state["status"] == "initialized"

    def test_synchronous_dispatch(self, mock_workflow_reducer):
        """Test synchronous action dispatch."""

        # Setup
        initial_state = {"counter": 0}
        action = {"type": "INCREMENT", "payload": {"amount": 1}}
        expected_state = {"counter": 1}

        mock_workflow_reducer.dispatch.return_value = expected_state

        # Test
        new_state = mock_workflow_reducer.dispatch(initial_state, action)

        # Verify
        assert new_state["counter"] == 1
        mock_workflow_reducer.dispatch.assert_called_once_with(initial_state, action)

    async def test_asynchronous_dispatch(self, mock_workflow_reducer):
        """Test asynchronous workflow dispatch."""

        # Setup
        initial_state = {"users": {}}
        action = {"type": "CREATE_USER", "payload": {"email": "test@example.com"}}

        expected_result = ProtocolNodeResult(
            value={"users": {"123": {"email": "test@example.com"}}},
            is_success=True,
            is_failure=False,
            events=[{"type": "user_created", "user_id": "123"}],
            context={"workflow_type": "user_creation"},
            error=None
        )

        mock_workflow_reducer.dispatch_async.return_value = expected_result

        # Test
        result = await mock_workflow_reducer.dispatch_async(initial_state, action)

        # Verify
        assert result.is_success is True
        assert len(result.events) == 1
        assert result.events[0]["type"] == "user_created"
        mock_workflow_reducer.dispatch_async.assert_called_once_with(initial_state, action)
```

## Performance Optimization

### Cache Performance Optimization

```python
import asyncio
from typing import Dict, Set
import time

class OptimizedCacheService:
    """Cache service with performance optimizations."""

    def __init__(self, base_cache: ProtocolCacheService):
        self.base_cache = base_cache
        self.local_cache: Dict[str, tuple] = {}  # key -> (value, timestamp, ttl)
        self.pending_sets: Dict[str, asyncio.Future] = {}
        self.batch_operations: Dict[str, Any] = {}
        self.batch_timer = None
        self.stats = {
            "local_hits": 0,
            "remote_hits": 0,
            "local_misses": 0,
            "remote_misses": 0,
            "batch_operations": 0
        }

    async def get(self, key: str) -> Optional[Any]:
        """Get with local cache layer."""

        # Check local cache first
        if key in self.local_cache:
            value, timestamp, ttl = self.local_cache[key]
            if ttl is None or time.time() - timestamp < ttl:
                self.stats["local_hits"] += 1
                return value
            else:
                # Expired, remove from local cache
                del self.local_cache[key]
                self.stats["local_misses"] += 1

        # Check remote cache
        value = await self.base_cache.get(key)
        if value is not None:
            # Cache locally for future requests
            self.local_cache[key] = (value, time.time(), 300)  # 5 minute local TTL
            self.stats["remote_hits"] += 1
        else:
            self.stats["remote_misses"] += 1

        return value

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set with deduplication and batching."""

        # Check for duplicate set operations
        if key in self.pending_sets:
            # Wait for existing operation
            try:
                return await self.pending_sets[key]
            except Exception:
                pass

        # Create future for this operation
        future = asyncio.Future()
        self.pending_sets[key] = future

        try:
            # Perform the set operation
            success = await self.base_cache.set(key, value, ttl_seconds)

            if success:
                # Update local cache
                local_ttl = min(ttl_seconds, 300) if ttl_seconds else 300
                self.local_cache[key] = (value, time.time(), local_ttl)

            future.set_result(success)
            return success

        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            # Clean up pending operation
            self.pending_sets.pop(key, None)

    async def batch_get(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple keys efficiently."""

        results = {}
        remote_keys = []

        # Check local cache first
        for key in keys:
            if key in self.local_cache:
                value, timestamp, ttl = self.local_cache[key]
                if ttl is None or time.time() - timestamp < ttl:
                    results[key] = value
                    self.stats["local_hits"] += 1
                    continue
                else:
                    del self.local_cache[key]

            remote_keys.append(key)

        # Batch fetch remaining keys from remote cache
        if remote_keys:
            # This would require extending the protocol for batch operations
            remote_tasks = [self.base_cache.get(key) for key in remote_keys]
            remote_results = await asyncio.gather(*remote_tasks, return_exceptions=True)

            for key, result in zip(remote_keys, remote_results):
                if not isinstance(result, Exception) and result is not None:
                    results[key] = result
                    # Cache locally
                    self.local_cache[key] = (result, time.time(), 300)
                    self.stats["remote_hits"] += 1
                else:
                    self.stats["remote_misses"] += 1

        return results

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""

        total_local = self.stats["local_hits"] + self.stats["local_misses"]
        total_remote = self.stats["remote_hits"] + self.stats["remote_misses"]

        local_hit_ratio = self.stats["local_hits"] / total_local if total_local > 0 else 0
        remote_hit_ratio = self.stats["remote_hits"] / total_remote if total_remote > 0 else 0

        return {
            "local_cache_size": len(self.local_cache),
            "local_hit_ratio": local_hit_ratio,
            "remote_hit_ratio": remote_hit_ratio,
            "pending_operations": len(self.pending_sets),
            "total_local_operations": total_local,
            "total_remote_operations": total_remote,
            **self.stats
        }

    async def cleanup_expired_local_cache(self) -> int:
        """Clean up expired local cache entries."""

        current_time = time.time()
        expired_keys = []

        for key, (value, timestamp, ttl) in self.local_cache.items():
            if ttl is not None and current_time - timestamp >= ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self.local_cache[key]

        return len(expired_keys)

# Usage
async def use_optimized_cache():
    """Example using optimized cache service."""

    base_cache = RedisCacheService(redis_client)
    optimized_cache = OptimizedCacheService(base_cache)

    # Test performance with repeated access
    test_keys = [f"user:{i}" for i in range(100)]
    test_data = {key: {"id": i, "name": f"User {i}"} for i, key in enumerate(test_keys)}

    # Set all data
    start_time = time.time()
    set_tasks = [
        optimized_cache.set(key, data)
        for key, data in test_data.items()
    ]
    await asyncio.gather(*set_tasks)
    set_time = time.time() - start_time

    # First batch get (remote cache)
    start_time = time.time()
    results1 = await optimized_cache.batch_get(test_keys)
    first_get_time = time.time() - start_time

    # Second batch get (local cache)
    start_time = time.time()
    results2 = await optimized_cache.batch_get(test_keys)
    second_get_time = time.time() - start_time

    # Performance statistics
    stats = optimized_cache.get_performance_stats()

    print(f"Performance Results:")
    print(f"  Set time: {set_time:.3f}s")
    print(f"  First get time: {first_get_time:.3f}s (remote)")
    print(f"  Second get time: {second_get_time:.3f}s (local)")
    print(f"  Speed improvement: {first_get_time / second_get_time:.1f}x")
    print(f"  Local hit ratio: {stats['local_hit_ratio']:.2%}")
    print(f"  Local cache size: {stats['local_cache_size']}")
```

## Best Practices

### Core Protocol Design Guidelines

1. **Type Safety**: Use strong typing throughout with minimal `Any` usage
2. **Async First**: Design protocols for async/await patterns with proper error handling
3. **Resource Management**: Include proper resource cleanup and connection management
4. **Observability**: Provide comprehensive metrics, statistics, and monitoring capabilities
5. **Extensibility**: Design protocols for extension without breaking changes
6. **Error Handling**: Use structured error types with detailed context information
7. **Performance**: Consider caching, batching, and optimization patterns in protocol design

### Error Handling Best Practices

1. **Structured Exceptions**: Use specific exception types for different error categories
2. **Context Preservation**: Include detailed context in error messages for debugging
3. **Graceful Degradation**: Design fallback mechanisms for service failures
4. **Resource Safety**: Ensure proper cleanup even in error conditions

The core protocols provide the essential system-level capabilities that enable all other ONEX framework operations with comprehensive caching, node coordination, configuration management, and workflow orchestration capabilities.
