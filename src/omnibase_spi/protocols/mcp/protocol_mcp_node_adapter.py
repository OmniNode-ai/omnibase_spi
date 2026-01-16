"""
MCP Node Adapter Protocol - ONEX SPI Interface.

Protocol definition for adapting ONEX nodes to MCP tools, enabling seamless
integration between the ONEX node execution model and the Model Context Protocol
tool ecosystem.

Domain: MCP tool adaptation and ONEX node integration
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_mcp_tool_types import (
    ProtocolMCPToolDefinition,
)

if TYPE_CHECKING:
    from omnibase_core.contracts.contract_base import ModelContractBase
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolMCPNodeAdapter(Protocol):
    """
    Protocol for adapting ONEX nodes to MCP tools.

    Provides a bridge between ONEX node contracts and MCP tool definitions,
    enabling ONEX nodes to be discovered and invoked as MCP tools. This adapter
    handles contract-to-tool conversion, parameter mapping, and execution routing.

    Key Features:
        - **Contract Conversion**: Transform ONEX node contracts into MCP tool definitions
        - **Dynamic Discovery**: Discover MCP-enabled nodes based on metadata tags
        - **Execution Bridge**: Invoke ONEX nodes using MCP tool invocation semantics
        - **Parameter Mapping**: Map MCP parameters to ONEX node inputs
        - **Correlation Tracking**: Maintain request correlation across systems

    Example:
        ```python
        class NodeToMCPAdapter:
            '''Adapter implementation for ONEX-to-MCP integration.'''

            async def node_to_tool_definition(
                self, contract: ModelContractBase
            ) -> ProtocolMCPToolDefinition:
                # Convert contract metadata to tool definition
                return ToolDefinition(
                    name=contract.name,
                    description=contract.description,
                    parameters=self._extract_parameters(contract),
                    ...
                )

            async def invoke_node_as_tool(
                self,
                tool_name: str,
                parameters: dict[str, ContextValue],
                correlation_id: UUID
            ) -> dict[str, ContextValue]:
                # Resolve node from tool name, execute, return result
                node = await self._resolve_node(tool_name)
                result = await node.execute(parameters)
                return result.to_context_values()

            async def discover_mcp_enabled_nodes(
                self, tags: list[str] | None
            ) -> list[ProtocolMCPToolDefinition]:
                # Discover nodes with MCP capability tags
                nodes = await self._registry.find_nodes_by_tags(tags or ["mcp-enabled"])
                return [await self.node_to_tool_definition(n.contract) for n in nodes]

        adapter = NodeToMCPAdapter()
        assert isinstance(adapter, ProtocolMCPNodeAdapter)

        # Convert a node contract to MCP tool
        tool_def = await adapter.node_to_tool_definition(my_compute_node.contract)

        # Invoke the node as an MCP tool
        result = await adapter.invoke_node_as_tool(
            tool_name="compute_embedding",
            parameters={"text": "hello world"},
            correlation_id=uuid4()
        )
        ```
    """

    async def node_to_tool_definition(
        self, contract: "ModelContractBase"
    ) -> ProtocolMCPToolDefinition:
        """
        Convert an ONEX node contract to an MCP tool definition.

        Transforms the node's contract metadata, input/output schemas, and
        execution parameters into an equivalent MCP tool definition that can
        be registered with MCP registries.

        Args:
            contract: The ONEX node contract to convert. Contains metadata
                about the node's capabilities, input/output schemas, and
                execution requirements.

        Returns:
            An MCP tool definition that represents the node's capabilities
            in MCP-compatible format, including parameter definitions,
            return schema, and execution endpoint.

        Raises:
            SPIError: If the contract cannot be converted to a valid tool
                definition (e.g., missing required metadata).
            ValidationError: If the contract schema is incompatible with
                MCP parameter types.

        Example:
            ```python
            contract = await node_registry.get_contract("compute_embedding")
            tool_def = await adapter.node_to_tool_definition(contract)
            print(f"Tool: {tool_def.name}, Parameters: {len(tool_def.parameters)}")
            ```
        """
        ...

    async def invoke_node_as_tool(
        self,
        tool_name: str,
        parameters: dict[str, "ContextValue"],
        correlation_id: UUID,
    ) -> dict[str, "ContextValue"]:
        """
        Invoke an ONEX node using MCP tool invocation semantics.

        Resolves the tool name to its corresponding ONEX node, maps the
        MCP parameters to node inputs, executes the node, and returns
        the result in MCP-compatible format.

        Args:
            tool_name: The MCP tool name corresponding to the ONEX node.
                This is typically the node's canonical name or a registered
                alias in the adapter's mapping.
            parameters: MCP-formatted input parameters as a dictionary of
                context values. These are mapped to the node's input schema.
            correlation_id: UUID for request correlation and tracing across
                the MCP and ONEX execution boundaries.

        Returns:
            The node execution result as a dictionary of context values,
            formatted for MCP tool response semantics.

        Raises:
            SPIError: If the tool name cannot be resolved to a node.
            ExecutionError: If the node execution fails.
            ValidationError: If the parameters do not match the node's
                expected input schema.

        Example:
            ```python
            result = await adapter.invoke_node_as_tool(
                tool_name="compute_embedding",
                parameters={"text": "machine learning basics", "model": "default"},
                correlation_id=uuid4()
            )
            embedding = result.get("embedding")
            print(f"Embedding dimension: {len(embedding)}")
            ```
        """
        ...

    async def discover_mcp_enabled_nodes(
        self, tags: list[str] | None
    ) -> list[ProtocolMCPToolDefinition]:
        """
        Discover ONEX nodes that are enabled for MCP tool exposure.

        Searches the node registry for nodes that have been tagged or
        configured for MCP exposure, converts their contracts to tool
        definitions, and returns them for registration.

        Args:
            tags: Optional list of tags to filter discovered nodes.
                If None, discovers all MCP-enabled nodes (typically those
                tagged with "mcp-enabled" or similar). Multiple tags are
                treated as an OR filter.

        Returns:
            A list of MCP tool definitions for all discovered nodes that
            match the filter criteria. Each definition is ready for
            registration with an MCP registry.

        Raises:
            SPIError: If the node registry is unavailable or the discovery
                operation fails.

        Example:
            ```python
            # Discover all MCP-enabled nodes
            all_tools = await adapter.discover_mcp_enabled_nodes(None)
            print(f"Found {len(all_tools)} MCP-enabled nodes")

            # Discover only compute nodes with specific tags
            compute_tools = await adapter.discover_mcp_enabled_nodes(
                tags=["compute", "embedding"]
            )
            for tool in compute_tools:
                print(f"  - {tool.name}: {tool.description}")
            ```
        """
        ...


__all__ = [
    "ProtocolMCPNodeAdapter",
]
