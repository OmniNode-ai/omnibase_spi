#!/usr/bin/env python3
"""
Node Registry Protocol - ONEX SPI Interface.

Protocol definition for node discovery and registration in distributed environments.
Supports the ONEX Messaging Design v0.3 with environment isolation and node groups.

Integrates with Consul-based discovery while maintaining clean protocol boundaries.
"""

from typing import Dict, List, Optional, Protocol, runtime_checkable

from omnibase.protocols.types.core_types import (
    ContextValue,
    HealthStatus,
    NodeType,
    ProtocolDateTime,
    ProtocolSemVer,
)


@runtime_checkable
class ProtocolNodeChangeCallback(Protocol):
    """Protocol for node change callback functions."""

    def __call__(self, node_info: "ProtocolNodeInfo", change_type: str) -> None:
        """Handle node registry changes."""
        ...


@runtime_checkable
class ProtocolWatchHandle(Protocol):
    """Protocol for watch handle objects."""

    watch_id: str
    is_active: bool


@runtime_checkable
class ProtocolNodeRegistryConfig(Protocol):
    """Protocol for node registry configuration."""

    consul_host: str
    consul_port: int
    consul_token: Optional[str]
    health_check_interval: int
    retry_attempts: int


@runtime_checkable
class ProtocolNodeInfo(Protocol):
    """Protocol for node information objects."""

    node_id: str
    node_type: NodeType
    node_name: str
    environment: str
    group: str
    version: ProtocolSemVer
    health_status: HealthStatus
    endpoint: str
    metadata: Dict[str, ContextValue]
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
        class RegistryConsulNode:
            def __init__(self, environment: str = "dev", consul_endpoint: str = "localhost:8500"):
                self.environment = environment
                self.consul = consul.Consul(host=consul_endpoint.split(':')[0],
                                          port=int(consul_endpoint.split(':')[1]))
                self.watches = {}

            async def register_node(self, node_info: ProtocolNodeInfo, ttl_seconds: int = 30) -> bool:
                # Register node in Consul with TTL health check
                service_id = f"{node_info.node_id}-{self.environment}"
                return await self.consul.agent.service.register(
                    name=f"{self.environment}-{node_info.group}-{node_info.node_type}",
                    service_id=service_id,
                    address=node_info.endpoint.split(':')[0],
                    port=int(node_info.endpoint.split(':')[1]),
                    tags=[node_info.group, str(node_info.version)],
                    meta=node_info.metadata,
                    check=consul.Check.ttl(f"{ttl_seconds}s")
                )

            async def discover_nodes(self, node_type: Optional[NodeType] = None,
                                   environment: Optional[str] = None,
                                   group: Optional[str] = None) -> List[ProtocolNodeInfo]:
                # Discover nodes from Consul catalog
                env = environment or self.environment
                service_filter = f"{env}-"
                if group:
                    service_filter += f"{group}-"
                if node_type:
                    service_filter += str(node_type)

                services = await self.consul.catalog.services()
                matching_nodes = []

                for service_name in services:
                    if service_name.startswith(service_filter):
                        service_info = await self.consul.catalog.service(service_name)
                        for node in service_info:
                            matching_nodes.append(self._convert_to_node_info(node))

                return matching_nodes

        # Usage in application
        registry: ProtocolNodeRegistry = RegistryConsulNode("prod", "consul.company.com:8500")

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
            registered_at=datetime.now(),
            last_heartbeat=datetime.now()
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
        async def on_node_change(node: ProtocolNodeInfo, change_type: str):
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

    def __init__(
        self,
        environment: str = "dev",
        consul_endpoint: Optional[str] = None,
        config: Optional[ProtocolNodeRegistryConfig] = None,
    ):
        """
        Initialize node registry.

        Args:
            environment: Environment name (dev, staging, prod)
            consul_endpoint: Optional Consul endpoint override
            config: Optional registry configuration protocol
        """
        ...

    async def register_node(
        self, node_info: ProtocolNodeInfo, ttl_seconds: int = 30
    ) -> bool:
        """
        Register a node in the registry.

        Args:
            node_info: Node information to register
            ttl_seconds: Time-to-live for registration

        Returns:
            True if registration successful
        """
        ...

    async def unregister_node(self, node_id: str) -> bool:
        """
        Unregister a node from the registry.

        Args:
            node_id: Node ID to unregister

        Returns:
            True if unregistration successful
        """
        ...

    async def update_node_health(
        self,
        node_id: str,
        health_status: HealthStatus,
        metadata: Dict[str, ContextValue],
    ) -> bool:
        """
        Update node health status.

        Args:
            node_id: Node ID to update
            health_status: New health status
            metadata: Health status metadata (required for proper monitoring)

        Returns:
            True if update successful
        """
        ...

    async def heartbeat(self, node_id: str) -> bool:
        """
        Send heartbeat for a registered node.

        Args:
            node_id: Node ID for heartbeat

        Returns:
            True if heartbeat accepted
        """
        ...

    async def discover_nodes(
        self,
        node_type: Optional[NodeType] = None,
        environment: Optional[str] = None,
        group: Optional[str] = None,
        health_filter: Optional[HealthStatus] = None,
    ) -> List[ProtocolNodeInfo]:
        """
        Discover nodes matching criteria.

        Args:
            node_type: Filter by node type
            environment: Filter by environment (default: current)
            group: Filter by node group
            health_filter: Filter by health status

        Returns:
            List of matching node information
        """
        ...

    async def get_node(self, node_id: str) -> Optional[ProtocolNodeInfo]:
        """
        Get specific node information.

        Args:
            node_id: Node ID to retrieve

        Returns:
            Node information or None if not found
        """
        ...

    async def get_nodes_by_group(self, group: str) -> List[ProtocolNodeInfo]:
        """
        Get all nodes in a node group.

        Args:
            group: Node group name

        Returns:
            List of nodes in the group
        """
        ...

    async def get_gateway_for_group(self, group: str) -> Optional[ProtocolNodeInfo]:
        """
        Get the Group Gateway node for a node group.

        Args:
            group: Node group name

        Returns:
            Gateway node info or None if no gateway
        """
        ...

    async def watch_node_changes(
        self,
        callback: ProtocolNodeChangeCallback,
        node_type: Optional[NodeType] = None,
        group: Optional[str] = None,
    ) -> ProtocolWatchHandle:
        """
        Watch for node registry changes.

        Args:
            callback: Function to call on changes
            node_type: Optional filter by node type
            group: Optional filter by group

        Returns:
            Watch handle for cleanup
        """
        ...

    async def stop_watch(self, watch_handle: ProtocolWatchHandle) -> None:
        """
        Stop watching node changes.

        Args:
            watch_handle: Handle returned by watch_node_changes
        """
        ...
