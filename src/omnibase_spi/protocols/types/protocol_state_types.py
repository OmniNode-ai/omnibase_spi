"""
State and action protocol types for ONEX SPI interfaces.

Domain: State management, actions, metadata, and system events.

This module contains protocol definitions for state management patterns,
action dispatching, metadata handling, and system event processing. These
protocols support reducer-style state management and event-driven architectures.

Protocols included:
- ProtocolMetadata: Structured metadata containers
- ProtocolMetadataOperations: Metadata access and mutation operations
- ProtocolActionPayload: Action payload with operation parameters
- ProtocolAction: Reducer action definitions
- ProtocolState: Reducer state containers
- ProtocolStateSystemEvent: State management system event definitions
- ProtocolInputState: ONEX input state for format conversion
- ProtocolOutputState: ONEX output state for conversion results
"""

from typing import Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_base_types import (
    ContextValue,
    ProtocolDateTime,
    ProtocolSemVer,
)

# ==============================================================================
# Metadata Protocols
# ==============================================================================


@runtime_checkable
class ProtocolMetadata(Protocol):
    """
    Protocol for structured metadata containers with versioning.

    Provides a standardized container for metadata with version tracking
    and timestamps. This is an attribute-based protocol for data
    compatibility with storage systems.

    Attributes:
        data: Key-value metadata storage.
        version: Semantic version of the metadata schema.
        created_at: When the metadata was created.
        updated_at: When last modified, None if never updated.

    Example:
        ```python
        class EntityMetadata:
            data: dict[str, ContextValue] = {
                "source": "api",
                "priority": 1,
                "tags": ["important", "reviewed"]
            }
            version: ProtocolSemVer = semver_impl
            created_at: ProtocolDateTime = created_datetime_impl
            updated_at: ProtocolDateTime | None = None

            async def validate_metadata(self) -> bool:
                return bool(self.data)

            def is_up_to_date(self) -> bool:
                return self.updated_at is None or self.updated_at >= self.created_at

        metadata = EntityMetadata()
        assert isinstance(metadata, ProtocolMetadata)
        ```
    """

    data: dict[str, "ContextValue"]
    version: "ProtocolSemVer"
    created_at: "ProtocolDateTime"
    updated_at: "ProtocolDateTime | None"

    async def validate_metadata(self) -> bool: ...

    def is_up_to_date(self) -> bool: ...


@runtime_checkable
class ProtocolMetadataOperations(Protocol):
    """
    Protocol for metadata operations providing service-level functionality.

    Defines method-based operations for metadata access and mutation.
    This is a service protocol for implementing metadata management
    functionality.

    Attributes:
        get_value: Async method to retrieve a value by key.
        has_key: Method to check if key exists.
        keys: Method to list all keys.
        update_value: Async method to set/update a value.

    Example:
        ```python
        class MetadataOperationsService:
            def __init__(self, metadata: ProtocolMetadata):
                self._metadata = metadata

            async def get_value(self, key: str) -> ContextValue:
                return self._metadata.data.get(key)

            def has_key(self, key: str) -> bool:
                return key in self._metadata.data

            def keys(self) -> list[str]:
                return list(self._metadata.data.keys())

            async def update_value(self, key: str, value: ContextValue) -> None:
                self._metadata.data[key] = value

        ops = MetadataOperationsService(metadata)
        assert isinstance(ops, ProtocolMetadataOperations)
        ```
    """

    async def get_value(self, key: str) -> ContextValue: ...

    def has_key(self, key: str) -> bool: ...

    def keys(self) -> list[str]: ...

    async def update_value(self, key: str, value: ContextValue) -> None: ...


# ==============================================================================
# Action Protocols
# ==============================================================================


@runtime_checkable
class ProtocolActionPayload(Protocol):
    """
    Protocol for action payload containing operation parameters.

    Contains the target, operation type, and parameters for a reducer
    action. Used for structured state mutation commands.

    Attributes:
        target_id: UUID of the target entity/resource.
        operation: Name of the operation to perform.
        parameters: Operation-specific parameters.

    Example:
        ```python
        from uuid import uuid4

        class UpdateUserPayload:
            target_id: UUID = uuid4()
            operation: str = "update_profile"
            parameters: dict[str, ContextValue] = {
                "name": "John Doe",
                "email": "john@example.com"
            }

            async def validate_payload(self) -> bool:
                return bool(self.operation)

            def has_valid_parameters(self) -> bool:
                return len(self.parameters) > 0

        payload = UpdateUserPayload()
        assert isinstance(payload, ProtocolActionPayload)
        ```
    """

    target_id: UUID
    operation: str
    parameters: dict[str, "ContextValue"]

    async def validate_payload(self) -> bool: ...

    def has_valid_parameters(self) -> bool: ...


@runtime_checkable
class ProtocolAction(Protocol):
    """
    Protocol for reducer actions in state management patterns.

    Represents a complete action with type, payload, and timestamp
    for reducer-style state management. Used for dispatching state
    changes across ONEX systems.

    Attributes:
        type: Action type identifier (e.g., "USER_UPDATE", "ORDER_CREATE").
        payload: Action payload with operation details.
        timestamp: When the action was created.

    Example:
        ```python
        class CreateOrderAction:
            type: str = "ORDER_CREATE"
            payload: ProtocolActionPayload = create_order_payload
            timestamp: ProtocolDateTime = datetime_impl

            async def validate_action(self) -> bool:
                return bool(self.type)

            def is_executable(self) -> bool:
                return self.payload.has_valid_parameters()

        action = CreateOrderAction()
        assert isinstance(action, ProtocolAction)
        ```
    """

    type: str
    payload: "ProtocolActionPayload"
    timestamp: "ProtocolDateTime"

    async def validate_action(self) -> bool: ...

    def is_executable(self) -> bool: ...


# ==============================================================================
# State Protocols
# ==============================================================================


@runtime_checkable
class ProtocolState(Protocol):
    """
    Protocol for reducer state containers in state management.

    Represents the current state with version tracking and metadata.
    Used as the state container in reducer patterns for immutable
    state management.

    Attributes:
        metadata: Associated metadata for the state.
        version: Incrementing version number for optimistic locking.
        last_updated: When the state was last modified.

    Example:
        ```python
        class ApplicationState:
            metadata: ProtocolMetadata = metadata_impl
            version: int = 42
            last_updated: ProtocolDateTime = datetime_impl

            async def validate_state(self) -> bool:
                return self.version > 0

            def is_consistent(self) -> bool:
                return self.metadata is not None

        state = ApplicationState()
        assert isinstance(state, ProtocolState)
        ```
    """

    metadata: "ProtocolMetadata"
    version: int
    last_updated: "ProtocolDateTime"

    async def validate_state(self) -> bool: ...

    def is_consistent(self) -> bool: ...


# ==============================================================================
# System Event Protocols
# ==============================================================================


@runtime_checkable
class ProtocolStateSystemEvent(Protocol):
    """
    Protocol for state management system events and notifications.

    Represents internal system events with type, payload, and source
    identification. Used for state-driven communication between
    ONEX components, particularly in reducer patterns and node results.

    Note:
        For event bus communication with correlation tracking and rich metadata,
        use ProtocolEventBusSystemEvent from protocol_event_bus_types.

    Attributes:
        type: Event type identifier (e.g., "service.started", "node.failed").
        payload: Event-specific data payload.
        timestamp: Unix timestamp of event occurrence.
        source: Identifier of the event source component.

    Example:
        ```python
        class ServiceStartedEvent:
            type: str = "service.started"
            payload: dict[str, ContextValue] = {
                "service_name": "api-gateway",
                "port": 8080
            }
            timestamp: float = 1699900000.0
            source: str = "service-manager"

            async def validate_system_event(self) -> bool:
                return bool(self.type and self.source)

            def is_well_formed(self) -> bool:
                return self.timestamp > 0

        event = ServiceStartedEvent()
        assert isinstance(event, ProtocolStateSystemEvent)
        ```
    """

    type: str
    payload: dict[str, "ContextValue"]
    timestamp: float
    source: str

    async def validate_system_event(self) -> bool: ...

    def is_well_formed(self) -> bool: ...


# ==============================================================================
# ONEX Input/Output State Protocols
# ==============================================================================


@runtime_checkable
class ProtocolInputState(Protocol):
    """
    Protocol for ONEX input state in format conversion operations.

    Used for format conversion and string transformation operations.
    Distinct from ProtocolWorkflowInputState which handles workflow
    orchestration.

    Attributes:
        input_string: The raw input string to be converted.
        source_format: Format of the input (e.g., "json", "yaml", "xml").
        metadata: Additional context for the conversion.

    Example:
        ```python
        class JsonToYamlInput:
            input_string: str = '{"key": "value"}'
            source_format: str = "json"
            metadata: dict[str, ContextValue] = {"encoding": "utf-8"}

            async def validate_onex_input(self) -> bool:
                return bool(self.input_string and self.source_format)

        input_state = JsonToYamlInput()
        assert isinstance(input_state, ProtocolInputState)
        ```
    """

    input_string: str
    source_format: str
    metadata: dict[str, "ContextValue"]

    async def validate_onex_input(self) -> bool:
        """
        Validate ONEX input state for format conversion.

        Returns:
            True if input string and source format are valid
        """
        ...


@runtime_checkable
class ProtocolOutputState(Protocol):
    """
    Protocol for ONEX output state from format conversion operations.

    Contains the result of a format conversion including the converted
    string, target format, and success status. Used as the return value
    from conversion operations.

    Attributes:
        output_string: The converted output string.
        target_format: Format of the output (e.g., "json", "yaml", "xml").
        conversion_success: Whether the conversion succeeded.
        metadata: Additional context from the conversion.

    Example:
        ```python
        class YamlConversionOutput:
            output_string: str = "key: value\\n"
            target_format: str = "yaml"
            conversion_success: bool = True
            metadata: dict[str, ContextValue] = {
                "lines": 1,
                "encoding": "utf-8"
            }

            async def validate_output_state(self) -> bool:
                return self.conversion_success or bool(self.output_string)

        output_state = YamlConversionOutput()
        assert isinstance(output_state, ProtocolOutputState)
        ```
    """

    output_string: str
    target_format: str
    conversion_success: bool
    metadata: dict[str, "ContextValue"]

    async def validate_output_state(self) -> bool: ...
