#!/usr/bin/env python3
"""
Node Registry Protocol - ONEX SPI Interface.

Protocol definition for node discovery and registration in distributed environments.
Supports the ONEX Messaging Design v0.3 with environment isolation and tool groups.

Integrates with Consul-based discovery while maintaining clean protocol boundaries.
"""

from typing import Dict, List, Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase.protocols.types.core_types import HealthStatus, NodeType, ProtocolDateTime, ProtocolSemVer


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
    metadata: Dict[str, object]
    registered_at: ProtocolDateTime
    last_heartbeat: ProtocolDateTime


@runtime_checkable
class ProtocolNodeRegistry(Protocol):
    """
    Protocol for node discovery and registration services.

    Supports the ONEX Messaging Design v0.3 patterns:
    - Environment isolation (dev, staging, prod)
    - Tool group mini-meshes
    - Consul-based discovery integration
    - Health monitoring and heartbeat tracking

    Implementations may use Consul, etcd, or other discovery backends.
    """

    def __init__(
        self, environment: str = "dev", consul_endpoint: Optional[str] = None, **config
    ):
        """
        Initialize node registry.

        Args:
            environment: Environment name (dev, staging, prod)
            consul_endpoint: Optional Consul endpoint override
            **config: Registry-specific configuration
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
        metadata: Optional[Dict[str, object]] = None,
    ) -> bool:
        """
        Update node health status.

        Args:
            node_id: Node ID to update
            health_status: New health status
            metadata: Optional health metadata

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
        node_type: Optional[EnumNodeType] = None,
        environment: Optional[str] = None,
        group: Optional[str] = None,
        health_filter: Optional[EnumHealthStatus] = None,
    ) -> List[ProtocolNodeInfo]:
        """
        Discover nodes matching criteria.

        Args:
            node_type: Filter by node type
            environment: Filter by environment (default: current)
            group: Filter by tool group
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
        Get all nodes in a tool group.

        Args:
            group: Tool group name

        Returns:
            List of nodes in the group
        """
        ...

    async def get_gateway_for_group(self, group: str) -> Optional[ProtocolNodeInfo]:
        """
        Get the Group Gateway node for a tool group.

        Args:
            group: Tool group name

        Returns:
            Gateway node info or None if no gateway
        """
        ...

    async def watch_node_changes(
        self,
        callback,
        node_type: Optional[EnumNodeType] = None,
        group: Optional[str] = None,
    ) -> object:
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

    async def stop_watch(self, watch_handle: object) -> None:
        """
        Stop watching node changes.

        Args:
            watch_handle: Handle returned by watch_node_changes
        """
        ...
