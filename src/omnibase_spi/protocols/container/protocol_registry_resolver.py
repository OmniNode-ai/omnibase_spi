"""Protocol for dynamic registry resolution and configuration loading."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.container.protocol_registry import ProtocolRegistry


@runtime_checkable
class ProtocolRegistryResolver(Protocol):
    """
    Protocol for dynamic registry resolution and configuration loading.

    Provides a clean interface for registry resolution without exposing
    implementation-specific details. This protocol enables testing, scenario-based
    configuration, and cross-component registry access while maintaining proper
    architectural boundaries and dependency injection patterns.

    The resolver supports both scenario-based configuration (loading from YAML files)
    and programmatic registry construction with fallback tools, enabling flexible
    registry management across development, testing, and production environments.

    Example:
        ```python
        resolver: "ProtocolRegistryResolver" = create_registry_resolver()

        # Scenario-based resolution (loads from YAML)
        registry = await resolver.resolve_registry(
            registry_class=MyRegistryClass,
            scenario_path="scenarios/production.yaml"
        )

        # Programmatic resolution (no scenario file)
        registry = await resolver.resolve_registry(
            registry_class=MyRegistryClass,
            scenario_path=None  # Will use default configuration
        )

        # Use resolved registry
        artifacts = await registry.get_artifacts()
        status = await registry.get_status()
        ```

    Key Features:
        - Scenario-based registry configuration from YAML files
        - Programmatic registry construction with defaults
        - Registry class instantiation with proper initialization
        - Configuration extraction from scenario files
        - Fallback tool registration for development/testing
        - Type-safe registry resolution with protocol compliance
        - Separation of configuration from implementation

    Scenario Configuration:
        Scenario YAML files can contain registry configuration in a config block:
        ```yaml
        config:
          registry_tools:
            - name: "node_processor"
              type: "processing"
          registry_configs:
            validation_enabled: true
            auto_discovery: true
        ```

    Resolution Workflow:
        1. Check if scenario_path is provided and valid
        2. Load scenario YAML if path exists
        3. Extract registry_tools and registry_configs from config block
        4. Construct registry instance with extracted configuration
        5. Register fallback tools if no scenario configuration exists
        6. Return fully initialized registry instance

    See Also:
        - ProtocolRegistry: Base registry protocol for operations
        - ProtocolConfigurationManager: Configuration loading and management
        - ProtocolArtifactContainer: Artifact storage and retrieval
    """

    async def resolve_registry(
        self, registry_class: type, scenario_path: str | None = None
    ) -> ProtocolRegistry:
        """
        Resolve a registry instance based on the provided parameters.

        Args:
            registry_class: The registry class to instantiate
            scenario_path: Optional path to scenario configuration
            logger: Optional logger for resolution operations
            fallback_tools: Optional fallback tools dictionary

        Returns:
            The resolved registry instance

        Note:
            If scenario_path is provided and valid, loads scenario YAML,
            extracts registry_tools or registry_configs from the config block,
            and returns a constructed registry instance. If not, constructs
            the registry and registers fallback_tools (if provided).
        """
        ...
