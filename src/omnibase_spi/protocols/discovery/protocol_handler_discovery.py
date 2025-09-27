# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-01-27T00:00:00.000000'
# description: "Protocol" for node discovery and registration
# entrypoint: python://protocol_node_discovery
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# last_modified_at: '2025-01-27T00:00:00.000000'
# lifecycle: active
# meta_type: protocol
# metadata_version: 0.1.0
# name: protocol_node_discovery.py
# namespace: python://omnibase_spi.protocol.protocol_node_discovery
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 00000000-0000-0000-0000-000000000000
# version: 1.0.0
# === /OmniNode:Metadata ===

"""
Protocol for node discovery and registration.

This protocol defines the interface for discovering and registering file type nodes
without requiring hardcoded imports in the core registry. It enables plugin-based
architecture where nodes can be discovered dynamically.
"""

from typing import TYPE_CHECKING, Protocol, Type, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.file_handling.protocol_file_type_handler import (
        ProtocolFileTypeHandler,
    )


@runtime_checkable
class ProtocolHandlerInfo(Protocol):
    """Protocol for node information objects."""

    node_class: Type["ProtocolFileTypeHandler"]
    name: str
    source: str  # "core", "runtime", "node-local", "plugin"
    priority: int
    extensions: list[str]
    special_files: list[str]
    metadata: dict[str, str | int | float | bool]


@runtime_checkable
class ProtocolHandlerDiscovery(Protocol):
    """
    Protocol for discovering file type nodes.

    Implementations of this protocol can discover nodes from various sources
    (entry points, configuration files, environment variables, etc.) without
    requiring hardcoded imports in the core registry.

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        class EntryPointNodeDiscovery:
            @property
            def group_name(self) -> str: ...

            @property
            def discovered_nodes(self) -> list[Any]: ...

            async def discover_nodes(self) -> list["ProtocolHandlerInfo"]:
                # Discover nodes from Python entry points
                ...

            def get_source_name(self) -> str:
                ...

        class ConfigFileNodeDiscovery:
            @property
            def config_path(self) -> Any: ...

            async def discover_nodes(self) -> list["ProtocolHandlerInfo"]:
                # Discover nodes from configuration file
                ...

            def get_source_name(self) -> str:
                ...

        class EnvironmentNodeDiscovery:
            @property
            def env_prefix(self) -> str: ...

            async def discover_nodes(self) -> list["ProtocolHandlerInfo"]:
                # Discover nodes from environment variables
                ...

            def get_source_name(self) -> str:
                ...

        # Usage in application
        registry: "ProtocolNodeDiscoveryRegistry" = NodeDiscoveryRegistryImpl()

        # Register multiple discovery sources
        entry_point_discovery: "ProtocolHandlerDiscovery" = EntryPointNodeDiscovery(group_name="your.entry.point.group")
        config_discovery: "ProtocolHandlerDiscovery" = ConfigFileNodeDiscovery(config_path="path/to/config.yaml")
        env_discovery: "ProtocolHandlerDiscovery" = EnvironmentNodeDiscovery(env_prefix="YOUR_NODE_PREFIX_")

        registry.register_discovery_source(entry_point_discovery)
        registry.register_discovery_source(config_discovery)
        registry.register_discovery_source(env_discovery)

        # Discover and register all nodes
        registry.discover_and_register_nodes()

        # Print discovered nodes
        ...
        ```

    Discovery Implementation Patterns:
        - Entry Points: Use setuptools entry points for plugin architecture
        - Configuration Files: YAML/JSON configuration with dynamic imports
        - Environment Variables: Runtime node registration via env vars
        - Directory Scanning: Automatic discovery from node directories
        - Metadata Caching: Cache node metadata for performance
        - Error Handling: Graceful fallback when nodes fail to load
    """

    async def discover_nodes(self) -> list["ProtocolHandlerInfo"]:
        """
        Discover available nodes.

        Returns:
            List of ProtocolHandlerInfo objects for discovered nodes
        """
        ...

    def get_source_name(self) -> str:
        """
        Get the name of this discovery source.

        Returns:
            Human-readable name for this discovery source
        """
        ...


@runtime_checkable
class ProtocolNodeDiscoveryRegistry(Protocol):
    """
    Protocol for node registries that support dynamic discovery.

    This protocol extends the basic node registry with discovery capabilities,
    allowing nodes to be registered from multiple sources without hardcoded imports.
        ...
    """

    async def register_discovery_source(
        self, discovery: "ProtocolHandlerDiscovery"
    ) -> None:
        """
        Register a node discovery source.

        Args:
            discovery: Handler discovery implementation
        """
        ...

    async def discover_and_register_nodes(self) -> None:
        """
        Discover and register nodes from all registered discovery sources.
        """
        ...

    async def register_node_info(self, node_info: "ProtocolHandlerInfo") -> None:
        """
        Register a node from ProtocolHandlerInfo.

        Args:
            node_info: Information about the node to register
        """
        ...
