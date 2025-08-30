# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-01-27T00:00:00.000000'
# description: Protocol for node discovery and registration
# entrypoint: python://protocol_node_discovery
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# last_modified_at: '2025-01-27T00:00:00.000000'
# lifecycle: active
# meta_type: protocol
# metadata_version: 0.1.0
# name: protocol_node_discovery.py
# namespace: python://omnibase.protocol.protocol_node_discovery
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

from typing import Any, Protocol, Type

from omnibase.protocols.file_handling.protocol_file_type_handler import (
    ProtocolFileTypeHandler,
)


class ProtocolHandlerInfo(Protocol):
    """Protocol for node information objects."""

    node_class: Type[ProtocolFileTypeHandler]
    name: str
    source: str  # "core", "runtime", "node-local", "plugin"
    priority: int
    extensions: list[str]
    special_files: list[str]
    metadata: dict[str, Any]


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

            def discover_nodes(self) -> list[ProtocolHandlerInfo]:
                # Discover nodes from Python entry points
                nodes = []

                try:
                    import pkg_resources
                    for entry_point in pkg_resources.iter_entry_points(self.group_name):
                        try:
                            node_class = entry_point.load()

                            # Create temporary instance to extract metadata
                            temp_instance = node_class()

                            node_info = HandlerInfo(
                                node_class=node_class,
                                name=entry_point.name,
                                source="entry_point",
                                priority=temp_instance.node_priority,
                                extensions=temp_instance.supported_extensions,
                                special_files=temp_instance.supported_filenames,
                                metadata={
                                    "entry_point": entry_point.name,
                                    "module": entry_point.module_name,
                                    "distribution": entry_point.dist.project_name,
                                    "version": str(entry_point.dist.version)
                                }
                            )
                            nodes.append(node_info)

                        except Exception as e:
                            print(f"Failed to load node {entry_point.name}: {e}")
                            continue

                except ImportError:
                    print("pkg_resources not available for entry point discovery")

                return nodes

            def get_source_name(self) -> str:
                return f"EntryPoint[{self.group_name}]"

        class ConfigFileNodeDiscovery:
            @property
            def config_path(self) -> Any: ...

            def discover_nodes(self) -> list[ProtocolHandlerInfo]:
                # Discover nodes from configuration file
                nodes = []

                if not self.config_path.exists():
                    return nodes

                try:
                    import yaml
                    with open(self.config_path) as f:
                        config = yaml.safe_load(f)

                    for node_config in config.get("nodes", []):
                        # Dynamically import node class
                        module_path = node_config["module"]
                        class_name = node_config["class"]

                        module = importlib.import_module(module_path)
                        node_class = getattr(module, class_name)

                        node_info = HandlerInfo(
                            node_class=node_class,
                            name=node_config["name"],
                            source="config_file",
                            priority=node_config.get("priority", 50),
                            extensions=node_config.get("extensions", []),
                            special_files=node_config.get("special_files", []),
                            metadata={
                                "config_file": str(self.config_path),
                                "module": module_path,
                                "class": class_name,
                                "enabled": node_config.get("enabled", True)
                            }
                        )

                        if node_info.metadata.get("enabled", True):
                            nodes.append(node_info)

                except Exception as e:
                    print(f"Failed to load nodes from config: {e}")

                return nodes

            def get_source_name(self) -> str:
                return f"ConfigFile[{self.config_path}]"

        class EnvironmentNodeDiscovery:
            @property
            def env_prefix(self) -> str: ...

            def discover_nodes(self) -> list[ProtocolHandlerInfo]:
                # Discover nodes from environment variables
                nodes = []

                for env_key, env_value in os.environ.items():
                    if not env_key.startswith(self.env_prefix):
                        continue

                    try:
                        # Environment format: {env_prefix}PYTHON=module.path:ClassName
                        node_name = env_key[len(self.env_prefix):].lower()
                        module_path, class_name = env_value.split(":")

                        module = importlib.import_module(module_path)
                        node_class = getattr(module, class_name)

                        # Extract metadata from temporary instance
                        temp_instance = node_class()

                        node_info = HandlerInfo(
                            node_class=node_class,
                            name=node_name,
                            source="environment",
                            priority=temp_instance.node_priority,
                            extensions=temp_instance.supported_extensions,
                            special_files=temp_instance.supported_filenames,
                            metadata={
                                "env_var": env_key,
                                "module": module_path,
                                "class": class_name,
                                "source": "environment_variable"
                            }
                        )
                        nodes.append(node_info)

                    except Exception as e:
                        print(f"Failed to load node from {env_key}: {e}")
                        continue

                return nodes

            def get_source_name(self) -> str:
                return f"Environment[{self.env_prefix}*]"

        # Usage in application
        registry: ProtocolNodeDiscoveryRegistry = NodeDiscoveryRegistryImpl()

        # Register multiple discovery sources
        entry_point_discovery: ProtocolHandlerDiscovery = EntryPointNodeDiscovery(group_name="your.entry.point.group")
        config_discovery: ProtocolHandlerDiscovery = ConfigFileNodeDiscovery(config_path="path/to/config.yaml")
        env_discovery: ProtocolHandlerDiscovery = EnvironmentNodeDiscovery(env_prefix="YOUR_NODE_PREFIX_")

        registry.register_discovery_source(entry_point_discovery)
        registry.register_discovery_source(config_discovery)
        registry.register_discovery_source(env_discovery)

        # Discover and register all nodes
        registry.discover_and_register_nodes()

        print("Discovered nodes from:")
        for source in [entry_point_discovery, config_discovery, env_discovery]:
            nodes = source.discover_nodes()
            print(f"  - {source.get_source_name()}: {len(nodes)} nodes")
            for node_info in nodes:
                print(f"    * {node_info.name} (priority: {node_info.priority})")
                print(f"      Extensions: {node_info.extensions}")
                print(f"      Source: {node_info.source}")
        ```

    Discovery Implementation Patterns:
        - Entry Points: Use setuptools entry points for plugin architecture
        - Configuration Files: YAML/JSON configuration with dynamic imports
        - Environment Variables: Runtime node registration via env vars
        - Directory Scanning: Automatic discovery from node directories
        - Metadata Caching: Cache node metadata for performance
        - Error Handling: Graceful fallback when nodes fail to load
    """

    def discover_nodes(self) -> list[ProtocolHandlerInfo]:
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


class ProtocolNodeDiscoveryRegistry(Protocol):
    """
    Protocol for node registries that support dynamic discovery.

    This protocol extends the basic node registry with discovery capabilities,
    allowing nodes to be registered from multiple sources without hardcoded imports.
    """

    def register_discovery_source(self, discovery: ProtocolHandlerDiscovery) -> None:
        """
        Register a node discovery source.

        Args:
            discovery: Handler discovery implementation
        """
        ...

    def discover_and_register_nodes(self) -> None:
        """
        Discover and register nodes from all registered discovery sources.
        """
        ...

    def register_node_info(self, node_info: ProtocolHandlerInfo) -> None:
        """
        Register a node from ProtocolHandlerInfo.

        Args:
            node_info: Information about the node to register
        """
        ...
