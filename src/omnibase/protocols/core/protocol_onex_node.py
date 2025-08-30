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
# namespace: python://omnibase.protocol.protocol_onex_node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: auto-generated
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Any, Protocol, Type


class ProtocolOnexNode(Protocol):
    """
    Protocol for ONEX node implementations that can be loaded by the tool loader.

    All ONEX nodes must implement these methods to be compatible with the
    dynamic tool loading system and container orchestration.

    This protocol defines the standard interface that tool_loader.py expects
    when loading and validating tools.
    """

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the node's main functionality.

        Args:
            *args: Positional arguments passed to the node
            **kwargs: Keyword arguments passed to the node

        Returns:
            Result of the node execution
        """
        ...

    def get_node_config(self) -> dict[str, Any]:
        """
        Get the node's configuration information.

        Returns:
            Dictionary containing node configuration details such as
            name, version, dependencies, capabilities, etc.
        """
        ...

    def get_input_type(self) -> Type[Any]:
        """
        Get the expected input data type for this node.

        Returns:
            Type class representing the expected input structure
        """
        ...

    def get_output_type(self) -> Type[Any]:
        """
        Get the expected output data type for this node.

        Returns:
            Type class representing the expected output structure
        """
        ...
