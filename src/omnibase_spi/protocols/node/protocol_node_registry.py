"""
Node Registry Protocol - ONEX SPI Interface.

Protocol definition for node discovery and registration in distributed environments.
Supports the ONEX Messaging Design v0.3 with environment isolation and node groups.

Integrates with Consul-based discovery while maintaining clean protocol boundaries.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralHealthStatus,
    LiteralNodeType,
    ProtocolDateTime,
    ProtocolSemVer,
)


@runtime_checkable
class ProtocolNodeChangeCallback(Protocol):
    """Protocol for node change callback functions."""

    async def __call__(
        self, node_info: "ProtocolNodeInfo", change_type: str
    ) -> None: ...


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
    consul_token: str | None
    health_check_interval: int
    retry_attempts: int


@runtime_checkable
class ProtocolNodeInfo(Protocol):
    """Protocol for node information objects."""

    node_id: str
    node_type: LiteralNodeType
    node_name: str
    environment: str
    group: str
    version: "ProtocolSemVer"
    health_status: "LiteralHealthStatus"
    endpoint: str
    metadata: dict[str, "ContextValue"]
    registered_at: "ProtocolDateTime"
    last_heartbeat: "ProtocolDateTime"


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
        self, node_info: "ProtocolNodeInfo", ttl_seconds: int
    ) -> bool: ...

    async def unregister_node(self, node_id: str) -> bool: ...

    async def update_node_health(
        self,
        node_id: str,
        health_status: "LiteralHealthStatus",
        metadata: dict[str, "ContextValue"],
    ) -> bool: ...

    async def heartbeat(self, node_id: str) -> bool: ...

    async def discover_nodes(
        self,
        node_type: "LiteralNodeType | None" = None,
        environment: str | None = None,
        group: str | None = None,
        health_filter: "LiteralHealthStatus | None" = None,
    ) -> list["ProtocolNodeInfo"]: ...

    async def get_node(self, node_id: str) -> ProtocolNodeInfo | None: ...

    async def get_nodes_by_group(self, group: str) -> list["ProtocolNodeInfo"]: ...

    async def get_gateway_for_group(self, group: str) -> ProtocolNodeInfo | None: ...

    async def watch_node_changes(
        self,
        callback: "ProtocolNodeChangeCallback",
        node_type: "LiteralNodeType | None" = None,
        group: str | None = None,
    ) -> ProtocolWatchHandle: ...

    async def stop_watch(self, watch_handle: "ProtocolWatchHandle") -> None: ...
