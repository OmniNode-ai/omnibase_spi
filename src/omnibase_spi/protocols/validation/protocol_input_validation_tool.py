"""
Protocol interface for input validation tools in ONEX ecosystem.

This protocol defines the interface for input validation tools that validate
event bus states, workflow inputs, and configuration data. Provides type-safe
contracts for validation operations across ONEX service components.

Domain: Validation and Input Processing
Author: ONEX Framework Team
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType
    from omnibase_spi.protocols.types import ProtocolSemVer


@runtime_checkable
class ProtocolKafkaEventBusInputState(Protocol):
    """
    Protocol for Kafka event bus input state validation.

    Defines the contract for Kafka event bus input state objects, providing
    type-safe validation and serialization capabilities for event processing.

    Key Properties:
        - event_type: Type of the event (e.g., 'workflow.started', 'task.completed')
        - payload: Event data payload as dictionary
        - headers: Event metadata headers
        - timestamp: Event timestamp for ordering and processing
        - validation: Built-in state validation capability
        - serialization: Dictionary conversion for processing

    Usage Example:
        ```python
        input_state: ProtocolKafkaEventBusInputState = SomeInputState()

        # Validate state integrity
        if input_state.validate():
            data = input_state.to_dict()
            process_event(data)
        else:
            handle_invalid_state()
        ```
    """

    event_type: str
    payload: "JsonType"
    headers: dict[str, str]
    timestamp: int

    def validate(self) -> bool: ...
    def to_dict(self) -> "JsonType":
        """
        Convert the input state to a dictionary representation.

        Returns:
            Dictionary representation of the state
        """
        ...


@runtime_checkable
class ProtocolKafkaEventBusOutputState(Protocol):
    """
    Protocol for Kafka event bus output state validation.

    Defines the contract for Kafka event bus output state objects, providing
    type-safe validation and serialization capabilities for event processing results.

    Key Properties:
        - success: Whether the processing was successful
        - error_message: Error details if processing failed
        - processed_events: Number of events processed
        - output_data: Processing results and output data
        - serialization: Dictionary conversion for result handling

    Usage Example:
        ```python
        output_state: ProtocolKafkaEventBusOutputState = SomeOutputState()

        # Check processing results
        if output_state.success:
            results = output_state.to_dict()
            handle_successful_processing(results)
        else:
            handle_processing_error(output_state.error_message)
        ```
    """

    success: bool
    error_message: str | None
    processed_events: int
    output_data: "JsonType"

    def to_dict(self) -> "JsonType":
        """
        Convert the output state to a dictionary representation.

        Returns:
            Dictionary representation of the state
        """
        ...


@runtime_checkable
class ProtocolInputValidationTool(Protocol):
    """
    Protocol interface for input validation tools in ONEX ecosystem.

    Defines the contract for input validation tools that validate event bus states,
    workflow inputs, configuration data, and other input types. Provides type-safe
    validation contracts with comprehensive error reporting.

    Key Features:
        - Event bus input state validation
        - Configuration and parameter validation
        - Type-safe validation contracts
        - Comprehensive error reporting
        - Integration with event processing pipelines
        - Support for semantic versioning

    Validation Capabilities:
        - Schema validation for structured data
        - Type checking and conversion
        - Business rule validation
        - Cross-field validation
        - Custom validation rules

    Usage Example:
        ```python
        validator: ProtocolInputValidationTool = SomeValidator()

        # Validate event bus input state
        input_data = {
            'event_type': 'workflow.started',
            'payload': {'workflow_id': '123'},
            'headers': {'source': 'orchestrator'},
            'timestamp': 1640995200
        }

        valid_state, error_state = validator.validate_input_state(
            input_state=input_data,
            semver='1.0.0',
            event_bus=event_bus
        )

        if valid_state:
            process_valid_event(valid_state)
        else:
            handle_validation_error(error_state)
        ```

    Integration Patterns:
        - Works with ONEX event processing pipelines
        - Integrates with workflow orchestration
        - Supports configuration validation
        - Provides detailed error reporting
        - Compatible with async processing patterns
    """

    async def validate_input_state(
        self,
        input_state: "JsonType",
        semver: "ProtocolSemVer",
        event_bus: object,
    ) -> tuple[
        ProtocolKafkaEventBusInputState | None, ProtocolKafkaEventBusOutputState | None
    ]:
        """
            ...
        Validates the input_state JsonType against ProtocolEventBusInputState.

        Performs comprehensive validation of input state data including:
        - Schema validation and type checking
        - Required field validation
        - Business rule validation
        - Cross-field dependency validation
        - Semantic version compatibility

        Args:
            input_state: Input state dictionary to validate
            semver: Semantic version for validation rules compatibility
            event_bus: Event bus instance for context and additional validation

        Returns:
            Tuple of (valid_state, error_state):
            - If valid: (ProtocolKafkaEventBusInputState, None)
            - If invalid: (None, ProtocolKafkaEventBusOutputState) with error details
        """
        ...
