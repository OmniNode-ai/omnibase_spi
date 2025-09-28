from typing import Any, Protocol, runtime_checkable

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

    def run(self, *args: Any, **kwargs: Any) -> Any: ...

    async def get_node_config(self) -> "ProtocolNodeConfiguration": ...

    async def get_input_model(self) -> type[Any]: ...

    async def get_output_model(self) -> type[Any]: ...
