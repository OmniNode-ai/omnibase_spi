"""
MCP Discovery Protocol - ONEX SPI Interface.

Protocol definition for MCP service discovery and coordination.
Enables dynamic discovery of MCP services and subsystems across the network.

Domain: MCP service discovery and network coordination
"""

from collections.abc import Callable
from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralHealthStatus,
)
from omnibase_spi.protocols.types.protocol_mcp_types import (
    LiteralMCPSubsystemType,
    ProtocolMCPDiscoveryInfo,
    ProtocolMCPSubsystemRegistration,
)


@runtime_checkable
class ProtocolMCPServiceDiscovery(Protocol):
    """
    Protocol for MCP service discovery operations.

    Handles discovery of MCP services across the network using
    various discovery mechanisms (DNS-SD, Consul, etcd, etc.).
    """

    async def discover_mcp_services(
        self, service_type: LiteralMCPSubsystemType | None, timeout_seconds: int
    ) -> list[ProtocolMCPDiscoveryInfo]: ...

    async def discover_registries(
        self, timeout_seconds: int
    ) -> list[ProtocolMCPDiscoveryInfo]: ...

    async def register_service_for_discovery(
        self, service_info: ProtocolMCPDiscoveryInfo, ttl_seconds: int
    ) -> bool: ...

    async def unregister_service_from_discovery(self, service_name: str) -> bool: ...

    async def monitor_service_changes(
        self,
        callback: Callable[[ProtocolMCPDiscoveryInfo], None],
        service_type: LiteralMCPSubsystemType | None,
    ) -> bool: ...


@runtime_checkable
class ProtocolMCPDiscovery(Protocol):
    """
    Comprehensive MCP discovery protocol for distributed service coordination.

    Provides complete discovery capabilities including service discovery,
    health monitoring, and automatic registry coordination.

    Key Features:
        - **Multi-Protocol Discovery**: Support DNS-SD, Consul, etcd, and other backends
        - **Health-Aware Discovery**: Filter services based on health status
        - **Registry Selection**: Intelligent selection of optimal registry
        - **Multi-Registry Coordination**: Coordinate multiple registries with various strategies
        - **Change Monitoring**: Real-time monitoring of network changes
        - **Geographic Awareness**: Region and location-aware service discovery
        - **Load Balancing**: Distribute load across discovered services
    """

    @property
    def service_discovery(self) -> ProtocolMCPServiceDiscovery: ...

    async def discover_available_subsystems(
        self,
        service_type: LiteralMCPSubsystemType | None,
        health_check: bool,
        timeout_seconds: int,
    ) -> list[ProtocolMCPSubsystemRegistration]: ...

    async def discover_available_tools(
        self,
        service_type: LiteralMCPSubsystemType | None,
        tool_tags: list[str] | None,
        health_check: bool,
    ) -> dict[str, list[str]]: ...

    async def find_optimal_registry(
        self, criteria: dict[str, str | int | float | bool] | None, timeout_seconds: int
    ) -> ProtocolMCPDiscoveryInfo | None: ...

    async def coordinate_multi_registry(
        self, registries: list[ProtocolMCPDiscoveryInfo], coordination_strategy: str
    ) -> dict[str, str | int | float | bool]: ...

    async def monitor_network_changes(
        self,
        callback: Callable[[ProtocolMCPDiscoveryInfo], None],
        service_types: list[LiteralMCPSubsystemType] | None,
        change_types: list[str] | None,
    ) -> bool: ...

    async def get_network_topology(
        self, include_health: bool | None = None
    ) -> dict[str, str | int | float | bool | list[str]]: ...

    async def test_service_connectivity(
        self, service_info: ProtocolMCPDiscoveryInfo, test_tools: bool
    ) -> dict[str, str | int | float | bool]: ...

    async def get_service_health_status(
        self, service_name: str
    ) -> LiteralHealthStatus | None: ...

    async def update_service_cache(
        self, force_refresh: bool, service_type: LiteralMCPSubsystemType | None
    ) -> int: ...

    async def configure_discovery_backend(
        self, backend_type: str, configuration: dict[str, ContextValue]
    ) -> bool: ...

    async def get_discovery_statistics(self) -> dict[str, str | int | float | bool]: ...
