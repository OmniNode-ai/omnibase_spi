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
- ProtocolSystemEvent: System event definitions
- ProtocolOnexInputState: ONEX input state for format conversion
- ProtocolOnexOutputState: ONEX output state for conversion results
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
    """Protocol for structured metadata - attribute-based for data compatibility."""

    data: dict[str, "ContextValue"]
    version: "ProtocolSemVer"
    created_at: "ProtocolDateTime"
    updated_at: "ProtocolDateTime | None"

    async def validate_metadata(self) -> bool: ...

    def is_up_to_date(self) -> bool: ...


@runtime_checkable
class ProtocolMetadataOperations(Protocol):
    """Protocol for metadata operations - method-based for services."""

    async def get_value(self, key: str) -> ContextValue: ...

    def has_key(self, key: str) -> bool: ...

    def keys(self) -> list[str]: ...

    async def update_value(self, key: str, value: ContextValue) -> None: ...


# ==============================================================================
# Action Protocols
# ==============================================================================


@runtime_checkable
class ProtocolActionPayload(Protocol):
    """Protocol for action payload with specific data."""

    target_id: UUID
    operation: str
    parameters: dict[str, "ContextValue"]

    async def validate_payload(self) -> bool: ...

    def has_valid_parameters(self) -> bool: ...


@runtime_checkable
class ProtocolAction(Protocol):
    """Protocol for reducer actions."""

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
    """Protocol for reducer state."""

    metadata: "ProtocolMetadata"
    version: int
    last_updated: "ProtocolDateTime"

    async def validate_state(self) -> bool: ...

    def is_consistent(self) -> bool: ...


# ==============================================================================
# System Event Protocols
# ==============================================================================


@runtime_checkable
class ProtocolSystemEvent(Protocol):
    """Protocol for system events."""

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
class ProtocolOnexInputState(Protocol):
    """
    Protocol for ONEX input state objects.

    Used for format conversion and string transformation operations.
    Distinct from ProtocolWorkflowInputState which handles workflow orchestration.
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
class ProtocolOnexOutputState(Protocol):
    """Protocol for ONEX output state objects."""

    output_string: str
    target_format: str
    conversion_success: bool
    metadata: dict[str, "ContextValue"]

    async def validate_output_state(self) -> bool: ...
