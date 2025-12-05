from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.node.protocol_node_configuration import (
        ProtocolNodeConfiguration,
    )
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


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
        def get_input_type(self) -> type["ContextValue"]: ...

        def get_output_type(self) -> type["ContextValue"]: ...

        # New (v2.0+)
        def get_input_model(self) -> type["ContextValue"]: ...

        def get_output_model(self) -> type["ContextValue"]: ...
        ```
    """

    def run(
        self, *args: "ContextValue", **kwargs: "ContextValue"
    ) -> "ContextValue": ...

    async def get_node_config(self) -> "ProtocolNodeConfiguration": ...

    async def get_input_model(self) -> type["ContextValue"]: ...

    async def get_output_model(self) -> type["ContextValue"]: ...
