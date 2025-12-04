"""
Workflow value protocol types for ONEX SPI interfaces.

Domain: Type-safe value wrappers for workflow data serialization and validation.
"""

from typing import Generic, Literal, Protocol, TypeVar, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue

# Literal type alias for retry policies
LiteralRetryPolicy = Literal["none", "fixed", "exponential", "linear", "custom"]


@runtime_checkable
class ProtocolWorkflowValue(Protocol):
    """Protocol for workflow data values supporting serialization and validation."""

    def serialize(self) -> dict[str, object]: ...

    async def validate(self) -> bool: ...

    async def get_type_info(self) -> str: ...


@runtime_checkable
class ProtocolWorkflowStringValue(ProtocolWorkflowValue, Protocol):
    """Protocol for string-based workflow values."""

    value: str

    async def get_string_length(self) -> int: ...

    def is_empty_string(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowStringListValue(ProtocolWorkflowValue, Protocol):
    """Protocol for string list workflow values."""

    value: list[str]

    async def get_list_length(self) -> int: ...

    def is_empty_list(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowStringDictValue(ProtocolWorkflowValue, Protocol):
    """Protocol for string dictionary workflow values."""

    value: dict[str, "ContextValue"]

    async def get_dict_keys(self) -> list[str]: ...

    def has_key(self, key: str) -> bool: ...


@runtime_checkable
class ProtocolWorkflowNumericValue(ProtocolWorkflowValue, Protocol):
    """Protocol for numeric workflow values (int or float)."""

    value: int | float

    def is_integer(self) -> bool: ...

    def is_positive(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowStructuredValue(ProtocolWorkflowValue, Protocol):
    """Protocol for structured workflow values with context data."""

    value: dict[str, "ContextValue"]

    async def get_structure_depth(self) -> int: ...

    def flatten_structure(self) -> dict[str, "ContextValue"]: ...


T_WorkflowValue = TypeVar("T_WorkflowValue", str, int, float, bool)


@runtime_checkable
class ProtocolTypedWorkflowData(Generic[T_WorkflowValue], Protocol):
    """Protocol for strongly typed workflow data values."""

    value: T_WorkflowValue

    async def get_type_name(self) -> str: ...

    def serialize_typed(self) -> dict[str, ContextValue]: ...


@runtime_checkable
class ProtocolRetryConfiguration(Protocol):
    """Protocol for retry configuration objects."""

    policy: LiteralRetryPolicy
    max_attempts: int
    initial_delay_seconds: float
    max_delay_seconds: float
    backoff_multiplier: float
    jitter_enabled: bool
    retryable_errors: list[str]
    non_retryable_errors: list[str]

    async def validate_retry_config(self) -> bool: ...

    def is_valid_policy(self) -> bool: ...
