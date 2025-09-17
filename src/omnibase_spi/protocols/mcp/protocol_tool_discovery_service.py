"""
Protocol for Tool Discovery Service.

Defines the interface for tool discovery, instantiation, and registry operations
for MCP (Model Context Protocol) tool coordination in distributed systems.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, Union, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.core_types import ProtocolMetadata
    from omnibase_spi.protocols.types.mcp_types import (
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
        # Implementation example (not part of SPI)
        class ToolDiscoveryServiceImpl:
            def resolve_tool_from_contract(self, metadata, registry, contract_path):
                # Load tool configuration from contract
                module_path = self.build_module_path_from_contract(contract_path)
                tool_class = self.discover_tool_class_from_module(module_path, metadata.get('tool_class'))
                return self.instantiate_tool_with_container(tool_class, registry)

        # Usage in application code
        discovery_service: ProtocolToolDiscoveryService = ToolDiscoveryServiceImpl()

        tool = discovery_service.resolve_tool_from_contract(
            metadata={'tool_class': 'MyTool'},
            registry=container,
            contract_path=Path('/path/to/contract.yaml')
        )
        ```
    """

    def resolve_tool_from_contract(
        self,
        metadata: "ProtocolMetadata",
        registry: object,
        contract_path: Path,
    ) -> "ProtocolToolInstance":
        """
        Resolve and instantiate tool from contract specification.

        Args:
            metadata: Contract metadata with tool specification
            registry: Registry/container for tool instantiation
            contract_path: Path to contract file for module resolution

        Returns:
            Instantiated tool instance

        Raises:
            ValueError: If contract metadata is invalid
            ImportError: If tool module cannot be imported
            RuntimeError: If tool resolution or instantiation fails
        """
        ...

    def discover_tool_class_from_module(
        self,
        module_path: str,
        tool_class_name: str,
    ) -> "ProtocolToolClass":
        """
        Discover tool class from module path.

        Args:
            module_path: Python module path (e.g., 'omnibase.tools.xyz.node')
            tool_class_name: Name of tool class to find

        Returns:
            Tool class type

        Raises:
            ImportError: If module import fails
            AttributeError: If class is not found in module
            ValueError: If module path is invalid or insecure
        """
        ...

    def instantiate_tool_with_container(
        self,
        tool_class: "ProtocolToolClass",
        container: object,
    ) -> "ProtocolToolInstance":
        """
        Instantiate tool with dependency injection container.

        Args:
            tool_class: Tool class to instantiate
            container: DI container for tool dependencies

        Returns:
            Instantiated tool instance

        Raises:
            TypeError: If tool_class is not a valid class
            RuntimeError: If tool instantiation fails
            ValueError: If container is invalid
        """
        ...

    def resolve_tool_from_registry(
        self,
        registry: object,
        tool_class_name: str,
    ) -> "ProtocolToolInstance | None":
        """
        Resolve tool from registry pattern.

        Args:
            registry: Legacy registry with tool resolution capabilities
            tool_class_name: Tool class name to resolve

        Returns:
            Tool instance or None if not found

        Note:
            Returns None for not found rather than raising exception
            to support graceful fallback patterns.
        """
        ...

    def build_module_path_from_contract(
        self,
        contract_path: Path,
    ) -> str:
        """
        Build module path from contract file path.

        Args:
            contract_path: Path to contract.yaml file

        Returns:
            Python module path for tool's node.py file

        Raises:
            ValueError: If contract path is invalid
            FileNotFoundError: If contract file does not exist
        """
        ...

    def validate_module_path(
        self,
        module_path: str,
    ) -> bool:
        """
        Validate module path for security and correctness.

        Args:
            module_path: Python module path to validate

        Returns:
            True if module path is valid and secure

        Note:
            Performs security validation to prevent path traversal
            and malicious module imports.
        """
        ...

    def convert_class_name_to_registry_key(
        self,
        class_name: str,
    ) -> str:
        """
        Convert tool class name to registry key format.

        Args:
            class_name: Tool class name (e.g., ToolContractValidator)

        Returns:
            Registry key in snake_case format (e.g., contract_validator)

        Note:
            Follows consistent naming conventions for registry key mapping.
        """
        ...
