"""
Protocol interface for file type handler registry in ONEX ecosystem.

This protocol defines the interface for file type handler registries that manage
file extension mappings, handler registration, and type-specific processing
contracts across ONEX service components.

Domain: File Handling and Processing
Author: ONEX Framework Team
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.file_handling.protocol_file_type_handler import (
        ProtocolFileProcessingTypeHandler,
    )
    from omnibase_spi.protocols.types import ContextValue


@runtime_checkable
class ProtocolFileTypeHandlerRegistry(Protocol):
    """
    Protocol interface for file type handler registries in ONEX ecosystem.

    Defines the contract for managing file type handlers, extension mappings,
    and type-specific processing across ONEX service components. Provides
    type-safe registration, lookup, and management capabilities.

    Key Features:
        - File extension to handler mapping
        - Special filename registration (e.g., 'node.onex.yaml')
        - Priority-based conflict resolution
        - Node-local handler extensions
        - Handler metadata management
        - Type-safe registration APIs
        - Test isolation support

    Handler Registration Patterns:
        - Extension-based: '.py', '.yaml', '.json'
        - Named handlers: 'custom_yaml', 'config_parser'
        - Special filenames: 'node.onex.yaml', 'workflow.json'
        - Priority-based: Higher priority wins conflicts
        - Override capabilities: Forced handler replacement

    Usage Example:
        ```python
        registry: ProtocolFileTypeHandlerRegistry = SomeRegistry()

        # Register extension-based handler
        await registry.register('.yaml', yaml_handler)

        # Register special filename handler
        await registry.register_special('node.onex.yaml', node_handler)

        # Enhanced registration with metadata
        await registry.register_handler(
            extension_or_name='.json',
            handler=json_handler,
            source=HandlerSourceEnum.CORE,
            priority=10,
            override=False
        )

        # Get handler for file
        handler = await registry.get_handler(str('config.yaml'))
        if handler:
            result = await handler.process_file(str('config.yaml'))
        ```

    Integration Patterns:
        - Works with ONEX file processing pipelines
        - Integrates with content type detection systems
        - Supports dynamic handler loading
        - Provides handler metadata for discovery
    """

    async def register(
        self, extension: str, handler: "ProtocolFileProcessingTypeHandler"
    ) -> None:
        """
        Register a handler for a file extension.

        Args:
            extension: File extension (e.g., '.py', '.yaml')
            handler: Handler instance that implements ProtocolFileTypeHandler
        """
        ...

    async def register_special(
        self, filename: str, handler: "ProtocolFileProcessingTypeHandler"
    ) -> None:
        """
        Register a handler for a canonical filename or role.

        Args:
            filename: Special filename (e.g., 'node.onex.yaml', 'workflow.json')
            handler: Handler instance that implements ProtocolFileTypeHandler
        """
        ...

    async def register_handler(
        self,
        extension_or_name: str,
        handler: "ProtocolFileProcessingTypeHandler | type[ProtocolFileProcessingTypeHandler]",
        source: str,
        priority: int | None = None,
        override: bool | None = None,
        **handler_kwargs: object,
    ) -> None:
        """
        Enhanced handler registration API supporting both extension-based and named registration.

        Args:
            extension_or_name: File extension (e.g., '.py') or handler name (e.g., 'custom_yaml')
            handler: Handler instance or handler class
            source: Source of registration (e.g., 'CORE', 'PLUGIN', 'CUSTOM')
            priority: Priority for conflict resolution (higher wins)
            override: Whether to override existing handlers
            **handler_kwargs: Arguments to pass to handler constructor if handler is a class
        """
        ...

    async def get_handler(
        self, path: str
    ) -> "ProtocolFileProcessingTypeHandler | None":
        """
        Return the handler for the given path, or None if unhandled.

        Args:
            path: File path to get handler for

        Returns:
            Handler instance or None if no handler registered
        """
        ...

    async def get_named_handler(
        self, name: str
    ) -> "ProtocolFileProcessingTypeHandler | None":
        """
        Get a handler by name.

        Args:
            name: Handler name to lookup

        Returns:
            Handler instance or None if not found
        """
        ...

    async def list_handlers(self) -> list[dict[str, "ContextValue"]]:
        """
        List all registered handlers with metadata.

        Returns:
            List of handler metadata dictionaries
        """
        ...

    async def handled_extensions(self) -> set[str]:
        """
        Return the set of handled file extensions.

        Returns:
            Set of file extensions (e.g., {'.py', '.yaml', '.json'})
        """
        ...

    async def handled_specials(self) -> set[str]:
        """
        Return the set of handled special filenames.

        Returns:
            Set of special filenames (e.g., {'node.onex.yaml', 'workflow.json'})
        """
        ...

    async def handled_names(self) -> set[str]:
        """
        Return the set of handled named handlers.

        Returns:
            Set of handler names
        """
        ...

    async def register_all_handlers(self) -> None:
        """Register all canonical handlers for this registry."""
        ...

    async def register_node_local_handlers(
        self,
        handlers: dict[
            str,
            "ProtocolFileProcessingTypeHandler | type[ProtocolFileProcessingTypeHandler]",
        ],
    ) -> None:
        """
        Convenience method for nodes to register their local handlers.

        Args:
            handlers: Dict mapping extensions/names to handler classes or instances
        """
        ...

    async def clear_registry(self) -> None:
        """Clear all handler registrations for test isolation (required for protocol-compliant testing)."""
        ...
