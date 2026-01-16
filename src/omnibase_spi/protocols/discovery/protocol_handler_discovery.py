"""
Protocol for handler discovery and registration.

This protocol defines the interface for discovering and registering file type handlers
without requiring hardcoded imports in the core registry. It enables plugin-based
architecture where handlers can be discovered dynamically.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType

    # Forward reference for file type handler protocol
    @runtime_checkable
    class ProtocolFileTypeHandler(Protocol):
        """
        Protocol for file type handlers.

        Defines the interface for handling specific file types in the ONEX system.

        Examples:
            ```python
            class JsonFileHandler:
                name: str | None = None
                extensions: list[str] = [".json"]
                special_files: list[str] = ["package.json"]
            ```
        """

        name: str
        extensions: list[str]
        special_files: list[str]


@runtime_checkable
class ProtocolHandlerInfo(Protocol):
    """
    Protocol for handler information.

    Contains metadata about discovered file type handlers including their
    capabilities, priority, and source information.

    Examples:
        ```python
        handler_info: ProtocolHandlerInfo
        assert handler_info.name == "json_handler"
        assert handler_info.source == "core"
        ```
    """

    handler_class: type["ProtocolFileTypeHandler"]
    name: str
    source: str
    priority: int
    extensions: list[str]
    special_files: list[str]
    metadata: "dict[str, JsonType]"


@runtime_checkable
class ProtocolHandlerDiscovery(Protocol):
    """
    Protocol for discovering file type handlers.

    Implementations of this protocol can discover handlers from various sources
    (entry points, configuration files, environment variables, etc.) without
    requiring hardcoded imports in the core registry.
    """

    async def discover_handlers(self) -> list["ProtocolHandlerInfo"]: ...
    async def get_source_name(self) -> str:
        """
        Get the name of this discovery source.

        Returns:
            Human-readable name for this discovery source
        """
        ...


@runtime_checkable
class ProtocolFileHandlerRegistry(Protocol):
    """
    Protocol for file handler registries that support dynamic discovery.

    This protocol extends the basic file handler registry with discovery capabilities,
    allowing file type handlers to be registered from multiple sources without hardcoded imports.
    """

    async def register_discovery_source(
        self, discovery: "ProtocolHandlerDiscovery"
    ) -> None:
        """
        Register a handler discovery source.

        Args:
            discovery: Handler discovery implementation
        """
        ...

    async def discover_and_register_handlers(self) -> None:
        """
        Discover and register handlers from all registered discovery sources.
        """
        ...

    async def register_handler_info(self, handler_info: "ProtocolHandlerInfo") -> None:
        """
            ...
        Register a handler from HandlerInfo.

        Args:
            handler_info: Information about the handler to register
        """
        ...
