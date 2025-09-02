#!/usr/bin/env python3
"""
MCP Discovery Protocol - ONEX SPI Interface.

Protocol definition for MCP service discovery and coordination.
Enables dynamic discovery of MCP services and subsystems across the network.

Domain: MCP service discovery and network coordination
"""

from typing import Any, Callable, Optional, Protocol, runtime_checkable

from omnibase.protocols.types.core_types import (
    ContextValue,
    HealthStatus,
    ProtocolDateTime,
)
from omnibase.protocols.types.mcp_types import (
    MCPConnectionStatus,
    MCPSubsystemType,
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
        self,
        service_type: Optional[MCPSubsystemType] = None,
        timeout_seconds: int = 10,
    ) -> list[ProtocolMCPDiscoveryInfo]:
        """
        Discover available MCP services on the network.

        Args:
            service_type: Optional filter by service type
            timeout_seconds: Discovery timeout

        Returns:
            List of discovered MCP services
        """
        ...

    async def discover_registries(
        self, timeout_seconds: int = 10
    ) -> list[ProtocolMCPDiscoveryInfo]:
        """
        Discover available MCP registries.

        Args:
            timeout_seconds: Discovery timeout

        Returns:
            List of discovered MCP registries
        """
        ...

    async def register_service_for_discovery(
        self,
        service_info: ProtocolMCPDiscoveryInfo,
        ttl_seconds: int = 300,
    ) -> bool:
        """
        Register a service for network discovery.

        Args:
            service_info: Service information to register
            ttl_seconds: Registration TTL

        Returns:
            True if registration successful
        """
        ...

    async def unregister_service_from_discovery(self, service_name: str) -> bool:
        """
        Unregister a service from discovery.

        Args:
            service_name: Name of service to unregister

        Returns:
            True if unregistration successful
        """
        ...

    async def monitor_service_changes(
        self,
        callback: Callable[[Any], Any],
        service_type: Optional[MCPSubsystemType] = None,
    ) -> bool:
        """
        Monitor for service discovery changes.

        Args:
            callback: Function to call on service changes
            service_type: Optional filter by service type

        Returns:
            True if monitoring started successfully
        """
        ...


@runtime_checkable
class ProtocolMCPDiscovery(Protocol):
    """
    Comprehensive MCP discovery protocol for distributed service coordination.

    Provides complete discovery capabilities including service discovery,
    health monitoring, and automatic registry coordination.

    Usage Example:
        ```python
        # Discovery implementation (not part of SPI)
        class MCPDiscoveryImpl:
            def __init__(self, discovery_backend: str = "mdns"):
                self.backend = discovery_backend
                self.discovered_services: dict[str, ProtocolMCPDiscoveryInfo] = {}
                self.service_health: dict[str, HealthStatus] = {}
                self.monitors: list[callable] = []

            async def discover_available_subsystems(
                self,
                service_type: Optional[MCPSubsystemType] = None,
                health_check: bool = True
            ) -> list[ProtocolMCPSubsystemRegistration]:
                # Discover services
                discovered = await self.service_discovery.discover_mcp_services(
                    service_type=service_type
                )

                subsystems = []
                for service in discovered:
                    if health_check:
                        # Perform health check
                        health = await self._check_service_health(service)
                        if health != "healthy":
                            continue

                    # Query service for registration info
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.get(
                                f"{service.service_url}/api/v1/info",
                                timeout=10
                            )

                            if response.status_code == 200:
                                info = response.json()
                                subsystem = self._convert_to_registration(info, service)
                                subsystems.append(subsystem)

                    except Exception as e:
                        print(f"Failed to query service {service.service_name}: {e}")
                        continue

                return subsystems

            async def find_optimal_registry(
                self,
                criteria: dict[str, Any] = None
            ) -> Optional[ProtocolMCPDiscoveryInfo]:
                # Discover all registries
                registries = await self.service_discovery.discover_registries()

                if not registries:
                    return None

                # Apply selection criteria
                criteria = criteria or {}
                best_registry = None
                best_score = -1

                for registry in registries:
                    # Check health
                    health = await self._check_service_health(registry)
                    if health != "healthy":
                        continue

                    # Calculate selection score
                    score = await self._calculate_registry_score(registry, criteria)
                    if score > best_score:
                        best_score = score
                        best_registry = registry

                return best_registry

            async def coordinate_multi_registry(
                self,
                registries: list[ProtocolMCPDiscoveryInfo],
                coordination_strategy: str = "primary_backup"
            ) -> dict[str, Any]:
                if coordination_strategy == "primary_backup":
                    # Select primary registry
                    primary = await self._select_primary_registry(registries)
                    backups = [r for r in registries if r != primary]

                    return {
                        "strategy": "primary_backup",
                        "primary": primary,
                        "backups": backups,
                        "failover_enabled": True
                    }

                elif coordination_strategy == "load_balanced":
                    # Configure load balancing
                    return {
                        "strategy": "load_balanced",
                        "registries": registries,
                        "load_balancer_config": {
                            "algorithm": "round_robin",
                            "health_check_interval": 30
                        }
                    }

                elif coordination_strategy == "federated":
                    # Configure federation
                    return {
                        "strategy": "federated",
                        "registries": registries,
                        "federation_config": {
                            "sync_interval": 60,
                            "conflict_resolution": "timestamp"
                        }
                    }

                else:
                    raise ValueError(f"Unknown coordination strategy: {coordination_strategy}")

        # Usage in MCP system
        discovery: ProtocolMCPDiscovery = MCPDiscoveryImpl()

        # Discover available subsystems
        subsystems = await discovery.discover_available_subsystems(
            service_type="analytics",
            health_check=True
        )
        print(f"Found {len(subsystems)} analytics subsystems")

        # Find optimal registry
        registry = await discovery.find_optimal_registry(
            criteria={"region": "us-west-2", "load_threshold": 0.8}
        )

        if registry:
            print(f"Selected registry: {registry.service_name} at {registry.service_url}")

        # Monitor for changes
        await discovery.monitor_network_changes(
            callback=lambda changes: print(f"Network changes: {changes}"),
            service_types=["compute", "analytics"]
        )

        # Coordinate multiple registries
        registries = await discovery.service_discovery.discover_registries()
        coordination = await discovery.coordinate_multi_registry(
            registries, "primary_backup"
        )
        print(f"Registry coordination: {coordination['strategy']}")
        ```

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
    def service_discovery(self) -> ProtocolMCPServiceDiscovery:
        """Get the service discovery backend implementation."""
        ...

    async def discover_available_subsystems(
        self,
        service_type: Optional[MCPSubsystemType] = None,
        health_check: bool = True,
        timeout_seconds: int = 30,
    ) -> list[ProtocolMCPSubsystemRegistration]:
        """
        Discover available MCP subsystems across the network.

        Args:
            service_type: Optional filter by subsystem type
            health_check: Whether to perform health checks
            timeout_seconds: Discovery timeout

        Returns:
            List of discovered and validated subsystems
        """
        ...

    async def discover_available_tools(
        self,
        service_type: Optional[MCPSubsystemType] = None,
        tool_tags: Optional[list[str]] = None,
        health_check: bool = True,
    ) -> dict[str, list[str]]:
        """
        Discover available tools across all subsystems.

        Args:
            service_type: Optional filter by subsystem type
            tool_tags: Optional filter by tool tags
            health_check: Whether to perform health checks

        Returns:
            Dictionary mapping subsystem IDs to their available tools
        """
        ...

    async def find_optimal_registry(
        self,
        criteria: Optional[dict[str, Any]] = None,
        timeout_seconds: int = 20,
    ) -> Optional[ProtocolMCPDiscoveryInfo]:
        """
        Find the optimal MCP registry based on selection criteria.

        Args:
            criteria: Selection criteria (load, region, capabilities, etc.)
            timeout_seconds: Discovery timeout

        Returns:
            Optimal registry information or None if none found
        """
        ...

    async def coordinate_multi_registry(
        self,
        registries: list[ProtocolMCPDiscoveryInfo],
        coordination_strategy: str = "primary_backup",
    ) -> dict[str, Any]:
        """
        Coordinate multiple MCP registries with specified strategy.

        Args:
            registries: List of registry services
            coordination_strategy: Coordination strategy (primary_backup, load_balanced, federated)

        Returns:
            Coordination configuration and status
        """
        ...

    async def monitor_network_changes(
        self,
        callback: Callable[[Any], Any],
        service_types: Optional[list[MCPSubsystemType]] = None,
        change_types: Optional[list[str]] = None,
    ) -> bool:
        """
        Monitor network for service changes and notify via callback.

        Args:
            callback: Function to call on network changes
            service_types: Optional filter by service types
            change_types: Optional filter by change types (added, removed, updated)

        Returns:
            True if monitoring started successfully
        """
        ...

    async def get_network_topology(self, include_health: bool = True) -> dict[str, Any]:
        """
        Get current network topology of MCP services.

        Args:
            include_health: Whether to include health status information

        Returns:
            Network topology information including services and connections
        """
        ...

    async def test_service_connectivity(
        self,
        service_info: ProtocolMCPDiscoveryInfo,
        test_tools: bool = False,
    ) -> dict[str, Any]:
        """
        Test connectivity and functionality of a discovered service.

        Args:
            service_info: Service to test
            test_tools: Whether to test individual tool endpoints

        Returns:
            Connectivity test results
        """
        ...

    async def get_service_health_status(
        self, service_name: str
    ) -> Optional[HealthStatus]:
        """
        Get current health status of a discovered service.

        Args:
            service_name: Name of the service

        Returns:
            Health status or None if service not found
        """
        ...

    async def update_service_cache(
        self,
        force_refresh: bool = False,
        service_type: Optional[MCPSubsystemType] = None,
    ) -> int:
        """
        Update the local cache of discovered services.

        Args:
            force_refresh: Force refresh even if cache is fresh
            service_type: Optional filter by service type

        Returns:
            Number of services updated in cache
        """
        ...

    async def configure_discovery_backend(
        self, backend_type: str, configuration: dict[str, ContextValue]
    ) -> bool:
        """
        Configure the discovery backend (DNS-SD, Consul, etcd, etc.).

        Args:
            backend_type: Type of discovery backend
            configuration: Backend-specific configuration

        Returns:
            True if configuration successful
        """
        ...

    async def get_discovery_statistics(self) -> dict[str, Any]:
        """
        Get discovery system statistics and metrics.

        Returns:
            Discovery statistics including cache hits, discovery latency, etc.
        """
        ...
