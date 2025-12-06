"""
Node Registry Protocol - ONEX SPI Interface.

Protocol definition for node discovery and registration in distributed environments.
Supports the ONEX Messaging Design v0.3 with environment isolation and node groups.

Integrates with Consul-based discovery while maintaining clean protocol boundaries.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralHealthStatus,
    LiteralNodeType,
    ProtocolDateTime,
    ProtocolSemVer,
)


@runtime_checkable
class ProtocolNodeChangeCallback(Protocol):
    """
    Protocol for node change notification callback functions.

    Defines the callback signature for receiving notifications when
    node state changes occur in the registry, enabling reactive
    handling of node additions, removals, and health changes.

    Example:
        ```python
        registry: ProtocolNodeRegistry = get_node_registry()

        async def on_node_change(node: ProtocolNodeInfo, change_type: str):
            if change_type == "added":
                print(f"New node: {node.node_name}")
            elif change_type == "unhealthy":
                print(f"Node unhealthy: {node.node_name}")
                await handle_node_failure(node)
            elif change_type == "removed":
                print(f"Node removed: {node.node_name}")

        handle = await registry.watch_node_changes(
            callback=on_node_change,
            node_type="COMPUTE"
        )
        ```

    See Also:
        - ProtocolNodeRegistry: Registry interface with watch methods
        - ProtocolNodeInfo: Node information passed to callback
        - ProtocolWatchHandle: Watch subscription handle
    """

    async def __call__(self, node_info: ProtocolNodeInfo, change_type: str) -> None: ...


@runtime_checkable
class ProtocolWatchHandle(Protocol):
    """
    Protocol for node registry watch subscription handle.

    Represents an active subscription to node change events, providing
    identification and status tracking for subscription management
    and cleanup.

    Attributes:
        watch_id: Unique identifier for this watch subscription
        is_active: Whether the subscription is currently active

    Example:
        ```python
        registry: ProtocolNodeRegistry = get_node_registry()

        handle = await registry.watch_node_changes(
            callback=my_callback,
            node_type="COMPUTE"
        )

        print(f"Watch ID: {handle.watch_id}")
        print(f"Active: {handle.is_active}")

        # Later, stop watching
        await registry.stop_watch(handle)
        ```

    See Also:
        - ProtocolNodeRegistry: Registry with watch methods
        - ProtocolNodeChangeCallback: Callback for changes
    """

    watch_id: str
    is_active: bool


@runtime_checkable
class ProtocolNodeRegistryConfig(Protocol):
    """
    Protocol for node registry configuration parameters.

    Defines connection settings and operational parameters for
    the node registry, typically backed by Consul or similar
    service discovery systems.

    Attributes:
        consul_host: Consul server hostname
        consul_port: Consul server port number
        consul_token: Optional Consul ACL token for authentication
        health_check_interval: Interval in seconds between health checks
        retry_attempts: Number of retry attempts for failed operations

    Example:
        ```python
        registry: ProtocolNodeRegistry = get_node_registry()
        config = registry.config

        if config:
            print(f"Consul: {config.consul_host}:{config.consul_port}")
            print(f"Health check interval: {config.health_check_interval}s")
            print(f"Retry attempts: {config.retry_attempts}")
        ```

    See Also:
        - ProtocolNodeRegistry: Registry using this configuration
        - ProtocolNodeInfo: Registered node information
    """

    consul_host: str
    consul_port: int
    consul_token: str | None
    health_check_interval: int
    retry_attempts: int


@runtime_checkable
class ProtocolNodeInfo(Protocol):
    """
    Protocol for registered node information and metadata.

    Represents a node registered in the ONEX node registry with
    complete identification, classification, health status, and
    operational metadata for service discovery and coordination.

    Attributes:
        node_id: Unique identifier for this node instance
        node_type: ONEX node type classification
        node_name: Human-readable node name
        environment: Deployment environment (dev, staging, prod)
        group: Node group for mini-mesh organization
        version: Semantic version of the node
        health_status: Current health status
        endpoint: Network endpoint for communication
        metadata: Additional node metadata and capabilities
        registered_at: Timestamp of initial registration
        last_heartbeat: Timestamp of most recent heartbeat

    Example:
        ```python
        registry: ProtocolNodeRegistry = get_node_registry()
        nodes = await registry.discover_nodes(
            node_type="COMPUTE",
            environment="prod",
            health_filter="healthy"
        )

        for node in nodes:
            print(f"Node: {node.node_name} ({node.node_id})")
            print(f"  Type: {node.node_type}")
            print(f"  Endpoint: {node.endpoint}")
            print(f"  Health: {node.health_status}")
            print(f"  Last heartbeat: {node.last_heartbeat}")
        ```

    See Also:
        - ProtocolNodeRegistry: Registry for node management
        - ProtocolNodeChangeCallback: Change notifications
    """

    node_id: str
    node_type: LiteralNodeType
    node_name: str
    environment: str
    group: str
    version: ProtocolSemVer
    health_status: LiteralHealthStatus
    endpoint: str
    metadata: dict[str, ContextValue]
    registered_at: ProtocolDateTime
    last_heartbeat: ProtocolDateTime


@runtime_checkable
class ProtocolNodeRegistry(Protocol):
    """
    Protocol for node discovery and registration services.

    Supports the ONEX Messaging Design v0.3 patterns:
    - Environment isolation (dev, staging, prod)
    - Node group mini-meshes
    - Consul-based discovery integration
    - Health monitoring and heartbeat tracking

    Implementations may use Consul, etcd, or other discovery backends.

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        # RegistryConsulNode would implement the protocol interface
        # All methods defined in the protocol contract

        # Usage in application
        registry: "ProtocolNodeRegistry" = RegistryConsulNode("prod", "consul.company.com:8500")

        # Register current node
        node_info = NodeInfo(
            node_id="worker-001",
            node_type="COMPUTE",
            node_name="Data Processor",
            environment="prod",
            group="analytics",
            version=ProtocolSemVer(1, 2, 3),
            health_status="healthy",
            endpoint="10.0.1.15:8080",
            metadata={"cpu_cores": 8, "memory_gb": 32},
            registered_at=datetime.now().isoformat(),
            last_heartbeat=datetime.now().isoformat()
        )

        success = await registry.register_node(node_info, ttl_seconds=60)
        if success:
            print(f"Registered {node_info.node_name} successfully")

        # Discover compute nodes in analytics group
        compute_nodes = await registry.discover_nodes(
            node_type="COMPUTE",
            environment="prod",
            group="analytics"
        )

        print(f"Found {len(compute_nodes)} compute nodes in analytics group")

        # Set up node change monitoring
        async def on_node_change(node: "ProtocolNodeInfo", change_type: str):
            print(f"Node {node.node_name} changed: {change_type}")
            if change_type == "unhealthy":
                # Implement failover logic
                await handle_node_failure(node)

        watch_handle = await registry.watch_node_changes(
            callback=on_node_change,
            node_type="COMPUTE",
            group="analytics"
        )

        # Send periodic heartbeats
        while True:
            await registry.heartbeat(node_info.node_id)
            await asyncio.sleep(30)  # Heartbeat every 30 seconds
        ```

    Node Discovery Patterns:
        - Environment-based isolation: `prod-analytics-COMPUTE`
        - Group-based discovery: Find all nodes in a node group
        - Health-based filtering: Only discover healthy nodes
        - Type-based filtering: Find specific node types (COMPUTE, ORCHESTRATOR, etc.)
        - Watch-based monitoring: Real-time notifications of node changes
    """

    @property
    def environment(self) -> str: ...

    @property
    def consul_endpoint(self) -> str | None: ...

    @property
    def config(self) -> ProtocolNodeRegistryConfig | None: ...

    async def register_node(
        self, node_info: ProtocolNodeInfo, ttl_seconds: int
    ) -> bool: ...

    async def unregister_node(self, node_id: str) -> bool: ...

    async def update_node_health(
        self,
        node_id: str,
        health_status: LiteralHealthStatus,
        metadata: dict[str, ContextValue],
    ) -> bool: ...

    async def heartbeat(self, node_id: str) -> bool: ...

    async def discover_nodes(
        self,
        node_type: LiteralNodeType | None = None,
        environment: str | None = None,
        group: str | None = None,
        health_filter: LiteralHealthStatus | None = None,
    ) -> list[ProtocolNodeInfo]: ...

    async def get_node(self, node_id: str) -> ProtocolNodeInfo | None: ...

    async def get_nodes_by_group(self, group: str) -> list[ProtocolNodeInfo]: ...

    async def get_gateway_for_group(self, group: str) -> ProtocolNodeInfo | None: ...

    async def watch_node_changes(
        self,
        callback: ProtocolNodeChangeCallback,
        node_type: LiteralNodeType | None = None,
        group: str | None = None,
    ) -> ProtocolWatchHandle: ...

    async def stop_watch(self, watch_handle: ProtocolWatchHandle) -> None: ...
