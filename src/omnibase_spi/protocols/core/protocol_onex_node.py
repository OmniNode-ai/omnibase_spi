# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-08-01T12:00:00.000000'
# description: Protocol for ONEX node implementations
# entrypoint: python://protocol_onex_node
# hash: auto-generated
# last_modified_at: '2025-08-01T12:00:00.000000'
# lifecycle: active
# meta_type: protocol
# metadata_version: 0.1.0
# name: protocol_onex_node.py
# namespace: python://omnibase_spi.protocol.protocol_onex_node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: auto-generated
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.core.protocol_node_configuration import (
        ProtocolNodeConfiguration,
    )


@runtime_checkable
class ProtocolOnexNode(Protocol):
    """
    Protocol for ONEX node implementations.

    All ONEX nodes must implement these methods to be compatible with the
    dynamic node loading system and container orchestration.

    This protocol defines the standard interface that node_loader.py expects
    when loading and validating nodes.

    Key Features:
        - Standard execution interface
        - Configuration metadata access
        - Input/output type definitions
        - Runtime compatibility validation

    Breaking Changes (v2.0):
        - get_input_type() → get_input_model() for clarity
        - get_output_type() → get_output_model() for clarity

    Migration Guide:
        For existing implementations, rename your methods:
        ```python
        # Old (v1.x)
        def get_input_type(self) -> type[Any]: ...
        def get_output_type(self) -> type[Any]: ...

        # New (v2.0+)
        def get_input_model(self) -> type[Any]: ...
        def get_output_model(self) -> type[Any]: ...
        ```
    """

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the node's main functionality.

        This is the primary entry point for node execution. The method should
        handle all necessary input validation, processing, and output generation.

        Args:
            *args: Positional arguments passed to the node
            **kwargs: Keyword arguments passed to the node

        Returns:
            Result of the node execution (type depends on node implementation)

        Raises:
            ValueError: If input arguments are invalid
            RuntimeError: If node execution fails
            TypeError: If input types don't match expected models
        """
        ...

    def get_node_config(self) -> "ProtocolNodeConfiguration":
        """
        Get the node's configuration information.

        Returns comprehensive metadata about the node including capabilities,
        dependencies, version information, and runtime requirements.

        Returns:
            NodeConfiguration containing node metadata such as:
            - name: Node identifier
            - version: Semantic version
            - dependencies: Required dependencies
            - capabilities: Node capabilities list
            - runtime_requirements: Runtime constraints

        Raises:
            RuntimeError: If configuration cannot be determined
        """
        ...

    def get_input_model(self) -> type[Any]:
        """
        Get the expected input model type for this node.

        BREAKING CHANGE: Renamed from get_input_type() in v2.0 for clarity.
        The "model" terminology better reflects that this defines data models,
        not just primitive types.

        This method returns the type class that defines the structure
        and validation rules for inputs to this node. Used for:
        - Input validation before execution
        - API documentation generation
        - Type checking in development

        Returns:
            Type class representing the expected input structure.
            Should be a Pydantic model or compatible structured type.

        Raises:
            NotImplementedError: If node doesn't define input model
            RuntimeError: If input model cannot be determined

        Migration:
            Replace get_input_type() calls with get_input_model()
        """
        ...

    def get_output_model(self) -> type[Any]:
        """
        Get the expected output model type for this node.

        BREAKING CHANGE: Renamed from get_output_type() in v2.0 for clarity.
        The "model" terminology better reflects that this defines data models,
        not just primitive types.

        This method returns the type class that defines the structure
        of outputs from this node. Used for:
        - Output validation after execution
        - API documentation generation
        - Type checking for downstream consumers

        Returns:
            Type class representing the expected output structure.
            Should be a Pydantic type or compatible structured type.

        Raises:
            NotImplementedError: If node doesn't define output type
            RuntimeError: If output type cannot be determined
        """
        ...
