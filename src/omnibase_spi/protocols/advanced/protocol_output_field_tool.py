from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue


@runtime_checkable
class ProtocolModelOnexField(Protocol):
    """
    Protocol for ONEX field model representation.

    Defines the structure for individual field values with type information,
    enabling type-safe field access and validation in ONEX workflows.

    Attributes:
        field_name: Name of the field
        field_value: Value stored in the field (any type)
        field_type: Type identifier for the field value
    """

    field_name: str
    field_value: Any
    field_type: str


@runtime_checkable
class ProtocolOutputFieldTool(Protocol):
    """
    Protocol for output field generation tools in ONEX workflows.

    Defines the contract for tools that transform state and input into
    structured output fields. Enables extensible field generation with
    type safety and state management capabilities.

    Example:
        ```python
        from omnibase_spi.protocols.advanced import ProtocolOutputFieldTool

        async def process_field(
            tool: ProtocolOutputFieldTool,
            state: dict[str, "ContextValue"],
            input_state: dict[str, Any]
        ) -> "ProtocolModelOnexField":
            # Generate output field from state transformation
            field = await tool(state, input_state)

            print(f"Generated field: {field.field_name}")
            print(f"Value: {field.field_value}")
            print(f"Type: {field.field_type}")

            return field
        ```

    Key Features:
        - State-driven field generation
        - Type-aware field transformations
        - Input state integration for context-aware processing
        - Extensible for custom field generation logic
        - Integration with ONEX workflow pipelines

    See Also:
        - ProtocolOutputFormatter: Output formatting and presentation
        - ProtocolStamperEngine: Metadata stamping and field enrichment
        - ProtocolContractAnalyzer: Contract-based field definition
    """

    async def __call__(
        self, state: Any, input_state_dict: dict[str, Any]
    ) -> "ProtocolModelOnexField": ...
