"""
Marker and base protocol types for ONEX SPI interfaces.

Domain: Marker protocols, serialization interfaces, and base capability protocols.

This module contains marker protocols that define minimal interfaces for
capability detection and type-safe composition. These protocols are used
throughout ONEX to enable consistent patterns for:
- Serialization and data export
- Object identification and naming
- Configuration and execution
- Metadata provision
- Property and schema validation
"""

from typing import Literal, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_base_types import (
    ContextValue,
    ProtocolSemVer,
)


# ==============================================================================
# Serialization Result Protocol
# ==============================================================================


@runtime_checkable
class ProtocolSerializationResult(Protocol):
    """
    Protocol for serialization operation results.

    Provides standardized results for serialization operations across
    ONEX services, including success status, serialized data, and
    error handling information.

    Key Features:
        - Success/failure indication
        - Serialized data as string format
        - Detailed error messages for debugging
        - Consistent result structure across services

    Usage:
        result = serializer.serialize(data)
        if result.success:
            send_data(result.data)
        else:
            logger.error(f"Serialization failed: {result.error_message}")
    """

    success: bool
    data: str
    error_message: str | None

    async def validate_serialization(self) -> bool: ...

    def has_data(self) -> bool: ...


# ==============================================================================
# Schema Protocol
# ==============================================================================


@runtime_checkable
class ProtocolSchemaObject(Protocol):
    """Protocol for schema data objects."""

    schema_id: str
    schema_type: str
    schema_data: dict[str, "ContextValue"]
    version: "ProtocolSemVer"
    is_valid: bool

    async def validate_schema(self) -> bool: ...

    def is_valid_schema(self) -> bool: ...


# ==============================================================================
# Marker Protocols for Property Values
# ==============================================================================


@runtime_checkable
class ProtocolSupportedPropertyValue(Protocol):
    """
    Protocol for values that can be stored as ONEX property values.

    This marker protocol defines the minimal interface that property values
    must implement to be compatible with the ONEX property system.
    Properties are used for node configuration, service parameters,
    and dynamic system settings.

    Key Features:
        - Marker interface for property value compatibility
        - Runtime type checking with sentinel attribute
        - Safe storage in property management systems
        - Compatible with configuration and parameter systems

    Usage:
        def set_property(key: str, value: "ProtocolSupportedPropertyValue"):
            if isinstance(value, ProtocolSupportedPropertyValue):
                property_store[key] = value
            else:
                raise TypeError("Value not compatible with property system")

    This is a marker interface with a sentinel attribute for runtime checks.
    """

    __omnibase_property_value_marker__: Literal[True]

    async def validate_for_property(self) -> bool: ...


# ==============================================================================
# Serializable Protocol
# ==============================================================================


@runtime_checkable
class ProtocolSerializable(Protocol):
    """
    Protocol for objects that can be serialized to dictionary format.

    Provides standardized serialization contract for ONEX objects that need
    to be persisted, transmitted, or cached. The model_dump method ensures
    consistent serialization across all ONEX services.

    Key Features:
        - Standardized serialization interface
        - Type-safe dictionary output
        - Compatible with JSON serialization
        - Consistent across all ONEX services

    Usage:
        class MyDataObject(ProtocolSerializable):
            def model_dump(self) -> dict[str, ContextValue]:
                return {
                    "id": self.id,
                    "name": self.name,
                    "active": self.is_active
                }

        # Serialize for storage
        obj = MyDataObject()
        serialized = obj.model_dump()
        json.dumps(serialized)  # Safe for JSON
    """

    def model_dump(
        self,
    ) -> dict[
        str,
        str
        | int
        | float
        | bool
        | list[str | int | float | bool]
        | dict[str, str | int | float | bool],
    ]: ...


# ==============================================================================
# Identifiable Protocol
# ==============================================================================


@runtime_checkable
class ProtocolIdentifiable(Protocol):
    """Protocol for objects that have an ID."""

    __omnibase_identifiable_marker__: Literal[True]

    @property
    def id(self) -> str: ...


# ==============================================================================
# Nameable Protocol
# ==============================================================================


@runtime_checkable
class ProtocolNameable(Protocol):
    """Protocol for objects that have a name."""

    __omnibase_nameable_marker__: Literal[True]

    @property
    def name(self) -> str: ...


# ==============================================================================
# Configurable Protocol
# ==============================================================================


@runtime_checkable
class ProtocolConfigurable(Protocol):
    """Protocol for objects that can be configured."""

    __omnibase_configurable_marker__: Literal[True]

    def configure(self, **kwargs: ContextValue) -> None: ...


# ==============================================================================
# Executable Protocol
# ==============================================================================


@runtime_checkable
class ProtocolExecutable(Protocol):
    """Protocol for objects that can be executed."""

    __omnibase_executable_marker__: Literal[True]

    async def execute(self) -> object: ...


# ==============================================================================
# Metadata Provider Protocol
# ==============================================================================


@runtime_checkable
class ProtocolMetadataProvider(Protocol):
    """Protocol for objects that provide metadata."""

    __omnibase_metadata_provider_marker__: Literal[True]

    async def get_metadata(self) -> dict[str, str | int | bool | float]: ...
