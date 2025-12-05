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
    """
    Protocol for schema data objects with validation capabilities.

    Represents a schema definition including its data, version, and
    validation state. Used for schema management, validation, and
    versioning across ONEX services.

    Attributes:
        schema_id: Unique identifier for the schema.
        schema_type: Type classification (e.g., "json-schema", "protobuf").
        schema_data: The actual schema definition.
        version: Semantic version of the schema.
        is_valid: Whether the schema passes validation.

    Example:
        ```python
        class JsonSchemaObject:
            schema_id: str
            schema_type: str
            schema_data: dict[str, ContextValue]
            version: ProtocolSemVer
            is_valid: bool

            async def validate_schema(self) -> bool:
                return self.is_valid

            def is_valid_schema(self) -> bool:
                return self.is_valid

        schema = JsonSchemaObject()
        schema.schema_id = "user-profile-v1"
        schema.schema_type = "json-schema"
        schema.schema_data = {
            "type": "object",
            "properties": {"name": {"type": "string"}}
        }
        schema.is_valid = True
        assert isinstance(schema, ProtocolSchemaObject)
        ```
    """

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
    """
    Marker protocol for objects that have a unique identifier.

    Provides a consistent interface for accessing object identifiers
    across ONEX services. The marker attribute enables runtime type
    checking for identifiable objects.

    Attributes:
        __omnibase_identifiable_marker__: Sentinel for runtime checking.
        id: Property returning the unique identifier string.

    Example:
        ```python
        from typing import Literal

        class IdentifiableEntity:
            __omnibase_identifiable_marker__: Literal[True] = True

            @property
            def id(self) -> str:
                return "entity-12345"

        entity = IdentifiableEntity()
        assert isinstance(entity, ProtocolIdentifiable)
        assert entity.id == "entity-12345"
        ```
    """

    __omnibase_identifiable_marker__: Literal[True]

    @property
    def id(self) -> str: ...


# ==============================================================================
# Nameable Protocol
# ==============================================================================


@runtime_checkable
class ProtocolNameable(Protocol):
    """
    Marker protocol for objects that have a human-readable name.

    Provides a consistent interface for accessing object names
    across ONEX services. Used for display, logging, and user
    interface purposes.

    Attributes:
        __omnibase_nameable_marker__: Sentinel for runtime checking.
        name: Property returning the human-readable name.

    Example:
        ```python
        from typing import Literal

        class NamedService:
            __omnibase_nameable_marker__: Literal[True] = True

            @property
            def name(self) -> str:
                return "User Authentication Service"

        service = NamedService()
        assert isinstance(service, ProtocolNameable)
        assert service.name == "User Authentication Service"
        ```
    """

    __omnibase_nameable_marker__: Literal[True]

    @property
    def name(self) -> str: ...


# ==============================================================================
# Configurable Protocol
# ==============================================================================


@runtime_checkable
class ProtocolConfigurable(Protocol):
    """
    Marker protocol for objects that support runtime configuration.

    Provides a consistent interface for configuring objects at runtime
    with keyword arguments. Used for dynamic service configuration
    and parameter injection.

    Attributes:
        __omnibase_configurable_marker__: Sentinel for runtime checking.
        configure: Method to apply configuration parameters.

    Example:
        ```python
        from typing import Literal

        class ConfigurableProcessor:
            __omnibase_configurable_marker__: Literal[True] = True
            timeout: int = 30

            def configure(self, **kwargs: ContextValue) -> None:
                if "timeout" in kwargs:
                    self.timeout = int(kwargs["timeout"])

        processor = ConfigurableProcessor()
        assert isinstance(processor, ProtocolConfigurable)
        processor.configure(timeout=60)
        ```
    """

    __omnibase_configurable_marker__: Literal[True]

    def configure(self, **kwargs: ContextValue) -> None: ...


# ==============================================================================
# Executable Protocol
# ==============================================================================


@runtime_checkable
class ProtocolExecutable(Protocol):
    """
    Marker protocol for objects that can be executed asynchronously.

    Provides a consistent interface for executable operations across
    ONEX services. The execute method returns the result of the
    operation as a generic object.

    Attributes:
        __omnibase_executable_marker__: Sentinel for runtime checking.
        execute: Async method to perform the execution.

    Example:
        ```python
        from typing import Literal

        class ExecutableTask:
            __omnibase_executable_marker__: Literal[True] = True

            async def execute(self) -> object:
                # Perform async operation
                return {"status": "completed", "result": 42}

        task = ExecutableTask()
        assert isinstance(task, ProtocolExecutable)
        result = await task.execute()
        ```
    """

    __omnibase_executable_marker__: Literal[True]

    async def execute(self) -> object: ...


# ==============================================================================
# Metadata Provider Protocol
# ==============================================================================


@runtime_checkable
class ProtocolMetadataProvider(Protocol):
    """
    Marker protocol for objects that provide metadata access.

    Provides a consistent interface for retrieving metadata from objects
    across ONEX services. The metadata is returned as a dictionary with
    primitive value types for serialization compatibility.

    Attributes:
        __omnibase_metadata_provider_marker__: Sentinel for runtime checking.
        get_metadata: Async method to retrieve metadata dictionary.

    Example:
        ```python
        from typing import Literal

        class MetadataEnabledNode:
            __omnibase_metadata_provider_marker__: Literal[True] = True
            _name: str = "processor-v1"
            _version: str = "1.0.0"

            async def get_metadata(self) -> dict[str, str | int | bool | float]:
                return {
                    "name": self._name,
                    "version": self._version,
                    "active": True,
                    "priority": 100
                }

        node = MetadataEnabledNode()
        assert isinstance(node, ProtocolMetadataProvider)
        metadata = await node.get_metadata()
        ```
    """

    __omnibase_metadata_provider_marker__: Literal[True]

    async def get_metadata(self) -> dict[str, str | int | bool | float]: ...
