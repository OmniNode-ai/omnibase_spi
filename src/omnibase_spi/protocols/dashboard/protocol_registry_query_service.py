"""
Protocol for Registry Query Service - Dashboard UI Support.

Defines the interface for querying the ONEX node registry to provide
read-only views of nodes, capabilities, and contracts for dashboard
display and UI components.

This protocol is designed specifically to support dashboard use cases
where the UI needs to display registry information without modifying
the underlying registry state. All operations are read-only queries
that return view models suitable for UI rendering.

Ticket Reference: OMN-1285 - Dashboard Protocols for omnibase_spi

Key Features:
    - Read-only access to node registry information
    - View model transformation for UI display
    - Capability enumeration and filtering
    - Contract inspection for node details
    - Filtered queries for large registries

Related Protocols:
    - ProtocolHandlerRegistry: Write operations for registry management
    - ProtocolServiceRegistry: Service-level dependency injection
    - ProtocolNodeCapability: Capability definitions (in protocol_workflow_execution_types)

Note:
    This protocol intentionally separates read concerns from write concerns
    to support the CQRS (Command Query Responsibility Segregation) pattern
    in dashboard implementations.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.contracts import ModelContractBase
    from omnibase_core.models.dashboard import ModelCapabilityView, ModelNodeView


@runtime_checkable
class ProtocolRegistryQueryService(Protocol):
    """
    Protocol for querying registry data for dashboard display.

    Provides read-only access to node registry information, transforming
    internal registry data into view models suitable for UI rendering.
    This protocol supports dashboard components that need to display
    lists of nodes, their capabilities, and contract details.

    All methods are asynchronous to support efficient data loading patterns
    in modern dashboard frameworks, enabling lazy loading and pagination
    of large datasets.

    Example Usage:
        ```python
        from typing import TYPE_CHECKING

        if TYPE_CHECKING:
            from omnibase_core.models.dashboard import ModelNodeView, ModelCapabilityView
            from omnibase_core.models.contracts import ModelContractBase

        class RegistryQueryServiceImpl:
            '''Concrete implementation of ProtocolRegistryQueryService.'''

            def __init__(self, registry: ProtocolHandlerRegistry) -> None:
                self._registry = registry

            async def list_nodes(self) -> Sequence[ModelNodeView]:
                # Transform registry entries to view models
                handlers = await self._registry.get_all_handlers()
                return [self._to_node_view(h) for h in handlers]

            async def list_capabilities(self) -> Sequence[ModelCapabilityView]:
                # Aggregate capabilities across all nodes
                capabilities = await self._registry.get_all_capabilities()
                return [self._to_capability_view(c) for c in capabilities]

            async def get_node_contract(
                self, node_id: str
            ) -> ModelContractBase | None:
                handler = await self._registry.get_handler(node_id)
                return handler.contract if handler else None

            async def get_node_by_id(
                self, node_id: str
            ) -> ModelNodeView | None:
                handler = await self._registry.get_handler(node_id)
                return self._to_node_view(handler) if handler else None

            async def filter_nodes(
                self, filter_criteria: dict[str, Any]
            ) -> Sequence[ModelNodeView]:
                handlers = await self._registry.query_handlers(filter_criteria)
                return [self._to_node_view(h) for h in handlers]

        # Usage in dashboard controller
        query_service: ProtocolRegistryQueryService = RegistryQueryServiceImpl(registry)
        nodes = await query_service.list_nodes()
        for node in nodes:
            print(f"Node: {node.name} - {node.status}")
        ```

    Thread Safety:
        Implementations MUST be thread-safe for concurrent read operations.
        Since all methods are read-only, no locking is typically required
        beyond what the underlying registry provides.

    Performance Considerations:
        - list_nodes() and list_capabilities() may return large datasets
        - Consider implementing pagination in the underlying implementation
        - Use filter_nodes() for targeted queries on large registries
        - Cache view models when registry data changes infrequently
    """

    async def list_nodes(self) -> Sequence[ModelNodeView]:
        """
        List all registered nodes as view models.

        Returns a sequence of node view models suitable for dashboard
        display, containing essential node information like name, type,
        status, and metadata.

        Returns:
            Sequence of ModelNodeView objects representing all registered nodes.
            The sequence may be empty if no nodes are registered.
            Order is implementation-specific but should be consistent.

        Raises:
            RegistryError: If the registry cannot be queried due to
                connection issues or internal errors.

        Example:
            ```python
            # List all nodes for dashboard display
            nodes = await query_service.list_nodes()

            # Render in UI
            for node in nodes:
                render_node_card(
                    name=node.name,
                    node_type=node.node_type,
                    status=node.status,
                    capabilities=node.capabilities
                )
            ```

        Note:
            For large registries, consider using filter_nodes() with
            pagination criteria instead of loading all nodes at once.
        """
        ...

    async def list_capabilities(self) -> Sequence[ModelCapabilityView]:
        """
        List all unique capabilities across registered nodes.

        Aggregates and returns a deduplicated sequence of capability
        view models, useful for building capability filters or displaying
        a capability catalog in the dashboard.

        Returns:
            Sequence of ModelCapabilityView objects representing all unique
            capabilities available across registered nodes.
            The sequence may be empty if no capabilities are defined.

        Raises:
            RegistryError: If the registry cannot be queried due to
                connection issues or internal errors.

        Example:
            ```python
            # Build capability filter dropdown
            capabilities = await query_service.list_capabilities()

            # Create filter options
            filter_options = [
                {"value": cap.capability_id, "label": cap.display_name}
                for cap in capabilities
            ]
            render_capability_filter(options=filter_options)
            ```

        Note:
            Capabilities are deduplicated across all nodes. If multiple
            nodes provide the same capability, it appears only once in
            the result with aggregated metadata.
        """
        ...

    async def get_node_contract(self, node_id: str) -> ModelContractBase | None:
        """
        Retrieve the contract for a specific node.

        Returns the full contract definition for a node, including
        input/output schemas, validation rules, and behavioral constraints.
        Useful for detailed node inspection views in the dashboard.

        Args:
            node_id: Unique identifier of the node whose contract to retrieve.
                Must be a valid node identifier from the registry.

        Returns:
            ModelContractBase if the node exists and has a contract defined.
            None if the node does not exist or has no contract.

        Raises:
            RegistryError: If the registry cannot be queried due to
                connection issues or internal errors.
            ValueError: If node_id is empty or malformed.

        Example:
            ```python
            # Display node contract details
            contract = await query_service.get_node_contract("node-compute-123")

            if contract:
                render_contract_view(
                    inputs=contract.input_schema,
                    outputs=contract.output_schema,
                    constraints=contract.constraints
                )
            else:
                render_not_found("Contract not available")
            ```

        Note:
            The contract provides the full specification of node behavior.
            For a simpler overview, use get_node_by_id() instead.
        """
        ...

    async def get_node_by_id(self, node_id: str) -> ModelNodeView | None:
        """
        Retrieve a single node view by its identifier.

        Returns a view model for a specific node, optimized for
        displaying detailed node information in the dashboard.

        Args:
            node_id: Unique identifier of the node to retrieve.
                Must be a valid node identifier from the registry.

        Returns:
            ModelNodeView if the node exists in the registry.
            None if no node with the given identifier exists.

        Raises:
            RegistryError: If the registry cannot be queried due to
                connection issues or internal errors.
            ValueError: If node_id is empty or malformed.

        Example:
            ```python
            # Load node details for detail view
            node = await query_service.get_node_by_id("node-effect-456")

            if node:
                render_node_detail_page(
                    name=node.name,
                    description=node.description,
                    node_type=node.node_type,
                    status=node.status,
                    metadata=node.metadata,
                    capabilities=node.capabilities
                )
            else:
                render_404_page("Node not found")
            ```

        Note:
            This method is more efficient than list_nodes() when you
            only need information about a single specific node.
        """
        ...

    async def filter_nodes(
        self, filter_criteria: dict[str, Any]
    ) -> Sequence[ModelNodeView]:
        """
        Query nodes matching specified filter criteria.

        Provides flexible filtering of nodes based on various criteria
        such as node type, status, capabilities, or custom metadata.
        Essential for large registries where loading all nodes is impractical.

        Args:
            filter_criteria: Dictionary of filter conditions. Supported keys
                are implementation-specific but commonly include:
                - "node_type": Filter by node type (e.g., "compute", "effect")
                - "status": Filter by node status (e.g., "active", "inactive")
                - "capabilities": Filter by capability IDs (list)
                - "tags": Filter by metadata tags (list)
                - "name_pattern": Filter by name pattern (glob or regex)
                - "limit": Maximum number of results to return (int)
                - "offset": Number of results to skip for pagination (int)

        Returns:
            Sequence of ModelNodeView objects matching the filter criteria.
            The sequence may be empty if no nodes match.
            Order is implementation-specific but should be consistent.

        Raises:
            RegistryError: If the registry cannot be queried due to
                connection issues or internal errors.
            ValueError: If filter_criteria contains invalid keys or values.

        Example:
            ```python
            # Filter nodes by type and status
            active_compute_nodes = await query_service.filter_nodes({
                "node_type": "compute",
                "status": "active",
                "limit": 20,
                "offset": 0
            })

            # Filter nodes by capability
            nodes_with_llm = await query_service.filter_nodes({
                "capabilities": ["llm-inference", "text-generation"]
            })

            # Search by name pattern
            matching_nodes = await query_service.filter_nodes({
                "name_pattern": "node-compute-*",
                "tags": ["production"]
            })
            ```

        Note:
            Filter criteria are combined with AND logic by default.
            For complex queries, implementations may support additional
            operators in the filter_criteria dictionary.
        """
        ...
