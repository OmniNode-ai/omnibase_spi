from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.container.protocol_registry import ProtocolRegistry


@runtime_checkable
class ProtocolRegistryResolver(Protocol):
    """
    Protocol for registry resolution operations.

    Provides a clean interface for registry resolution without exposing
    implementation-specific details. This protocol enables testing and
    cross-component registry resolution while maintaining proper architectural boundaries.
    """

    async def resolve_registry(
        self, registry_class: type, scenario_path: str | None = None
    ) -> "ProtocolRegistry":
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
