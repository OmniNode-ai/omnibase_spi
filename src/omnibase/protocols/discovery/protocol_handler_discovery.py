# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-01-27T00:00:00.000000'
# description: Protocol for handler discovery and registration
# entrypoint: python://protocol_handler_discovery
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# last_modified_at: '2025-01-27T00:00:00.000000'
# lifecycle: active
# meta_type: protocol
# metadata_version: 0.1.0
# name: protocol_handler_discovery.py
# namespace: python://omnibase.protocol.protocol_handler_discovery
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
Protocol for handler discovery and registration.

This protocol defines the interface for discovering and registering file type handlers
without requiring hardcoded imports in the core registry. It enables plugin-based
architecture where handlers can be discovered dynamically.
"""

from typing import Any, Dict, List, Protocol, Type

from omnibase.protocols.file_handling.protocol_file_type_handler import (
    ProtocolFileTypeHandler,
)


class ProtocolHandlerInfo(Protocol):
    """Protocol for handler information objects."""

    handler_class: Type[ProtocolFileTypeHandler]
    name: str
    source: str  # "core", "runtime", "node-local", "plugin"
    priority: int
    extensions: List[str]
    special_files: List[str]
    metadata: Dict[str, Any]


class ProtocolHandlerDiscovery(Protocol):
    """
    Protocol for discovering file type handlers.

    Implementations of this protocol can discover handlers from various sources
    (entry points, configuration files, environment variables, etc.) without
    requiring hardcoded imports in the core registry.
    """

    def discover_handlers(self) -> List[ProtocolHandlerInfo]:
        """
        Discover available handlers.

        Returns:
            List of ProtocolHandlerInfo objects for discovered handlers
        """
        ...

    def get_source_name(self) -> str:
        """
        Get the name of this discovery source.

        Returns:
            Human-readable name for this discovery source
        """
        ...


class ProtocolHandlerRegistry(Protocol):
    """
    Protocol for handler registries that support dynamic discovery.

    This protocol extends the basic handler registry with discovery capabilities,
    allowing handlers to be registered from multiple sources without hardcoded imports.
    """

    def register_discovery_source(self, discovery: ProtocolHandlerDiscovery) -> None:
        """
        Register a handler discovery source.

        Args:
            discovery: Handler discovery implementation
        """
        ...

    def discover_and_register_handlers(self) -> None:
        """
        Discover and register handlers from all registered discovery sources.
        """
        ...

    def register_handler_info(self, handler_info: ProtocolHandlerInfo) -> None:
        """
        Register a handler from ProtocolHandlerInfo.

        Args:
            handler_info: Information about the handler to register
        """
        ...
