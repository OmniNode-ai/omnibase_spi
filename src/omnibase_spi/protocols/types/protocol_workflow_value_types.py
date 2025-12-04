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
    """
    Base protocol for workflow data values supporting serialization and validation.

    Provides the foundation for all typed workflow values in ONEX, enabling
    consistent serialization to dictionaries and validation of data integrity.
    All workflow value types inherit from this protocol to ensure uniform
    handling across distributed workflow systems.

    Key Features:
        - Dictionary serialization for cross-service data transfer
        - Async validation for complex validation rules
        - Type introspection for runtime type checking

    Example:
        ```python
        class WorkflowDataValue:
            def serialize(self) -> dict[str, object]:
                return {"type": "custom", "data": self._data}

            async def validate(self) -> bool:
                return self._data is not None

            async def get_type_info(self) -> str:
                return "WorkflowDataValue"

        value = WorkflowDataValue()
        assert isinstance(value, ProtocolWorkflowValue)
        serialized = value.serialize()
        is_valid = await value.validate()
        ```
    """

    def serialize(self) -> dict[str, object]: ...

    async def validate(self) -> bool: ...

    async def get_type_info(self) -> str: ...


@runtime_checkable
class ProtocolWorkflowStringValue(ProtocolWorkflowValue, Protocol):
    """
    Protocol for string-based workflow values with length and emptiness checks.

    Extends ProtocolWorkflowValue to provide specialized handling for string
    data in workflows. Enables efficient string manipulation, validation, and
    length checking for text-based workflow parameters and results.

    Attributes:
        value: The string value wrapped by this protocol.

    Example:
        ```python
        class StringWorkflowValue:
            def __init__(self, val: str):
                self.value = val

            async def get_string_length(self) -> int:
                return len(self.value)

            def is_empty_string(self) -> bool:
                return len(self.value) == 0

            def serialize(self) -> dict[str, object]:
                return {"type": "string", "value": self.value}

            async def validate(self) -> bool:
                return isinstance(self.value, str)

            async def get_type_info(self) -> str:
                return "string"

        value = StringWorkflowValue("hello")
        assert isinstance(value, ProtocolWorkflowStringValue)
        assert await value.get_string_length() == 5
        assert not value.is_empty_string()
        ```
    """

    value: str

    async def get_string_length(self) -> int: ...

    def is_empty_string(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowStringListValue(ProtocolWorkflowValue, Protocol):
    """
    Protocol for string list workflow values with collection operations.

    Extends ProtocolWorkflowValue to provide specialized handling for lists
    of strings in workflows. Commonly used for tags, categories, identifiers,
    and other multi-value string data in distributed workflow systems.

    Attributes:
        value: The list of string values wrapped by this protocol.

    Example:
        ```python
        class StringListWorkflowValue:
            def __init__(self, vals: list[str]):
                self.value = vals

            async def get_list_length(self) -> int:
                return len(self.value)

            def is_empty_list(self) -> bool:
                return len(self.value) == 0

            def serialize(self) -> dict[str, object]:
                return {"type": "string_list", "values": self.value}

            async def validate(self) -> bool:
                return all(isinstance(v, str) for v in self.value)

            async def get_type_info(self) -> str:
                return "string_list"

        tags = StringListWorkflowValue(["python", "onex", "workflow"])
        assert isinstance(tags, ProtocolWorkflowStringListValue)
        assert await tags.get_list_length() == 3
        assert not tags.is_empty_list()
        ```
    """

    value: list[str]

    async def get_list_length(self) -> int: ...

    def is_empty_list(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowStringDictValue(ProtocolWorkflowValue, Protocol):
    """
    Protocol for string-keyed dictionary workflow values with key operations.

    Extends ProtocolWorkflowValue to provide specialized handling for
    dictionaries with string keys and context values. Used for configuration
    data, metadata mappings, and structured key-value pairs in workflows.

    Attributes:
        value: Dictionary mapping string keys to context values.

    Example:
        ```python
        class DictWorkflowValue:
            def __init__(self, data: dict[str, ContextValue]):
                self.value = data

            async def get_dict_keys(self) -> list[str]:
                return list(self.value.keys())

            def has_key(self, key: str) -> bool:
                return key in self.value

            def serialize(self) -> dict[str, object]:
                return {"type": "dict", "data": self.value}

            async def validate(self) -> bool:
                return all(isinstance(k, str) for k in self.value.keys())

            async def get_type_info(self) -> str:
                return "string_dict"

        config = DictWorkflowValue({"host": "localhost", "port": 8080})
        assert isinstance(config, ProtocolWorkflowStringDictValue)
        assert config.has_key("host")
        assert "port" in await config.get_dict_keys()
        ```
    """

    value: dict[str, "ContextValue"]

    async def get_dict_keys(self) -> list[str]: ...

    def has_key(self, key: str) -> bool: ...


@runtime_checkable
class ProtocolWorkflowNumericValue(ProtocolWorkflowValue, Protocol):
    """
    Protocol for numeric workflow values supporting both integers and floats.

    Extends ProtocolWorkflowValue to provide specialized handling for numeric
    data in workflows. Supports type checking and sign validation for numeric
    parameters such as counts, measurements, thresholds, and scores.

    Attributes:
        value: The numeric value (int or float) wrapped by this protocol.

    Example:
        ```python
        class NumericWorkflowValue:
            def __init__(self, val: int | float):
                self.value = val

            def is_integer(self) -> bool:
                return isinstance(self.value, int)

            def is_positive(self) -> bool:
                return self.value > 0

            def serialize(self) -> dict[str, object]:
                return {"type": "numeric", "value": self.value}

            async def validate(self) -> bool:
                return isinstance(self.value, (int, float))

            async def get_type_info(self) -> str:
                return "integer" if self.is_integer() else "float"

        score = NumericWorkflowValue(95.5)
        assert isinstance(score, ProtocolWorkflowNumericValue)
        assert not score.is_integer()
        assert score.is_positive()
        ```
    """

    value: int | float

    def is_integer(self) -> bool: ...

    def is_positive(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowStructuredValue(ProtocolWorkflowValue, Protocol):
    """
    Protocol for structured workflow values with hierarchical context data.

    Extends ProtocolWorkflowValue to provide specialized handling for
    nested structured data in workflows. Supports depth analysis and
    flattening operations for complex configuration and state objects.

    Attributes:
        value: Dictionary containing nested context values.

    Example:
        ```python
        class StructuredWorkflowValue:
            def __init__(self, data: dict[str, ContextValue]):
                self.value = data

            async def get_structure_depth(self) -> int:
                def depth(d: dict, level: int = 0) -> int:
                    if not isinstance(d, dict):
                        return level
                    return max((depth(v, level + 1) for v in d.values()), default=level)
                return depth(self.value)

            def flatten_structure(self) -> dict[str, ContextValue]:
                result = {}
                def flatten(d: dict, prefix: str = ""):
                    for k, v in d.items():
                        key = f"{prefix}.{k}" if prefix else k
                        if isinstance(v, dict):
                            flatten(v, key)
                        else:
                            result[key] = v
                flatten(self.value)
                return result

            def serialize(self) -> dict[str, object]:
                return {"type": "structured", "data": self.value}

            async def validate(self) -> bool:
                return isinstance(self.value, dict)

            async def get_type_info(self) -> str:
                return "structured"

        nested = StructuredWorkflowValue({"db": {"host": "localhost", "port": 5432}})
        assert isinstance(nested, ProtocolWorkflowStructuredValue)
        flat = nested.flatten_structure()
        assert "db.host" in flat
        ```
    """

    value: dict[str, "ContextValue"]

    async def get_structure_depth(self) -> int: ...

    def flatten_structure(self) -> dict[str, "ContextValue"]: ...


T_WorkflowValue = TypeVar("T_WorkflowValue", str, int, float, bool)


@runtime_checkable
class ProtocolTypedWorkflowData(Generic[T_WorkflowValue], Protocol):
    """
    Generic protocol for strongly typed workflow data values with type safety.

    Provides type-safe workflow data handling using Python generics. Constrains
    the value type to primitive types (str, int, float, bool) for predictable
    serialization and cross-service compatibility in distributed workflows.

    Attributes:
        value: The typed value (str, int, float, or bool) wrapped by this protocol.

    Type Parameters:
        T_WorkflowValue: One of str, int, float, or bool.

    Example:
        ```python
        class TypedStringData:
            def __init__(self, val: str):
                self.value: str = val

            async def get_type_name(self) -> str:
                return type(self.value).__name__

            def serialize_typed(self) -> dict[str, ContextValue]:
                return {"type": "str", "value": self.value}

        class TypedIntData:
            def __init__(self, val: int):
                self.value: int = val

            async def get_type_name(self) -> str:
                return "int"

            def serialize_typed(self) -> dict[str, ContextValue]:
                return {"type": "int", "value": self.value}

        str_data = TypedStringData("hello")
        int_data = TypedIntData(42)
        assert isinstance(str_data, ProtocolTypedWorkflowData)
        assert isinstance(int_data, ProtocolTypedWorkflowData)
        assert await str_data.get_type_name() == "str"
        ```
    """

    value: T_WorkflowValue

    async def get_type_name(self) -> str: ...

    def serialize_typed(self) -> dict[str, ContextValue]: ...


@runtime_checkable
class ProtocolRetryConfiguration(Protocol):
    """
    Protocol for comprehensive retry configuration in distributed workflows.

    Defines retry behavior for workflow operations including policy type,
    attempt limits, delay strategies, and error classification. Supports
    multiple backoff strategies for resilient distributed system operation.

    Attributes:
        policy: Retry policy type (none, fixed, exponential, linear, custom).
        max_attempts: Maximum number of retry attempts allowed.
        initial_delay_seconds: Initial delay before first retry.
        max_delay_seconds: Maximum delay between retries (caps backoff).
        backoff_multiplier: Multiplier for exponential/linear backoff.
        jitter_enabled: Whether to add randomness to retry delays.
        retryable_errors: List of error types that should trigger retry.
        non_retryable_errors: List of error types that should not retry.

    Example:
        ```python
        class RetryConfig:
            policy: LiteralRetryPolicy = "exponential"
            max_attempts: int = 3
            initial_delay_seconds: float = 1.0
            max_delay_seconds: float = 30.0
            backoff_multiplier: float = 2.0
            jitter_enabled: bool = True
            retryable_errors: list[str] = ["TimeoutError", "ConnectionError"]
            non_retryable_errors: list[str] = ["ValidationError"]

            async def validate_retry_config(self) -> bool:
                return self.max_attempts > 0 and self.initial_delay_seconds >= 0

            def is_valid_policy(self) -> bool:
                return self.policy in ("none", "fixed", "exponential", "linear", "custom")

        config = RetryConfig()
        assert isinstance(config, ProtocolRetryConfiguration)
        assert config.is_valid_policy()
        assert await config.validate_retry_config()
        ```
    """

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
