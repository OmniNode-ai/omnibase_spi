"""
Protocol for Tool Discovery Service.

Defines the interface for tool discovery, instantiation, and registry operations
for MCP (Model Context Protocol) tool coordination in distributed systems.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ProtocolMetadata
    from omnibase_spi.protocols.types.protocol_mcp_types import (
        ProtocolToolClass,
        ProtocolToolInstance,
    )


@runtime_checkable
class ProtocolToolDiscoveryService(Protocol):
    """
    Protocol interface for tool discovery service operations.

    Provides duck typing interface for tool class discovery, validation,
    instantiation, and registry resolution in MCP-compliant systems.

    Key Features:
        - Tool resolution from contract specifications
        - Dynamic tool class discovery from modules
        - Container-based tool instantiation
        - Registry-based tool resolution
        - Secure module path validation
        - Tool metadata management

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        discovery_service: "ProtocolToolDiscoveryService" = get_tool_discovery_service()

        # Resolve tool from contract specification
        tool = discovery_service.resolve_tool_from_contract(
            metadata={'tool_class': 'MyTool'},
            registry=container,
            contract_path='/path/to/contract.yaml'
        )

        # Discover tool class from module path
        tool_class = discovery_service.discover_tool_class_from_module(
            module_path='tools.processing',
            tool_class_name='DataProcessor'
        )

        # All operations use protocol interface without exposing implementation
        # Enables flexible tool discovery and instantiation patterns
        ```
    """

    async def resolve_tool_from_contract(
        self, metadata: "ProtocolMetadata", registry: object, contract_path: str
    ) -> "ProtocolToolInstance": ...

    async def discover_tool_class_from_module(
        self, module_path: str, tool_class_name: str
    ) -> "ProtocolToolClass": ...

    def instantiate_tool_with_container(
        self, tool_class: "ProtocolToolClass", container: object
    ) -> "ProtocolToolInstance": ...

    def resolve_tool_from_registry(
        self, registry: object, tool_class_name: str
    ) -> "ProtocolToolInstance | None": ...

    async def build_module_path_from_contract(self, contract_path: str) -> str: ...

    async def validate_module_path(self, module_path: str) -> bool: ...

    async def convert_class_name_to_registry_key(self, class_name: str) -> str: ...
