"""
Pure SPI Protocol definitions for validation utilities.

This module contains only Protocol definitions for validation interfaces,
following SPI purity principles. Concrete implementations have been moved
to the utils/omnibase_spi_validation package.
"""

from typing import Protocol, TypeVar, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue

T = TypeVar("T")
P = TypeVar("P")


@runtime_checkable
class ProtocolValidationError(Protocol):
    """
    Protocol for validation error object representation.

    Encapsulates a single validation error with type classification,
    message content, contextual information, and severity level
    for structured error handling and reporting.

    Attributes:
        error_type: Classification of error (naming, structure, etc.)
        message: Human-readable error description
        context: Dictionary of contextual information
        severity: Severity level (critical, error, warning)

    Example:
        ```python
        result: ProtocolValidationResult = await validator.validate_implementation(
            impl, ProtocolExample
        )

        for error in result.errors:
            print(f"[{error.severity}] {error.error_type}: {error.message}")
            if error.context:
                print(f"  Context: {error.context}")
            print(str(error))
        ```

    See Also:
        - ProtocolValidationResult: Container for errors
        - ProtocolValidator: Error generation source
    """

    error_type: str
    message: str
    context: dict[str, ContextValue]
    severity: str

    def __str__(self) -> str: ...


@runtime_checkable
class ProtocolValidationResult(Protocol):
    """
    Protocol for protocol validation result object representation.

    Captures the complete outcome of validating an implementation
    against a protocol, including validity status, errors, warnings,
    and methods for result building and summarization.

    Attributes:
        is_valid: Whether implementation satisfies the protocol
        protocol_name: Name of the protocol being validated against
        implementation_name: Name of the implementation being validated
        errors: List of validation errors found
        warnings: List of validation warnings found

    Example:
        ```python
        validator: ProtocolValidator = get_validator()
        result = await validator.validate_implementation(my_impl, ProtocolExample)

        print(f"Valid: {result.is_valid}")
        print(f"Protocol: {result.protocol_name}")
        print(f"Implementation: {result.implementation_name}")
        print(f"Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")

        summary = await result.get_summary()
        print(summary)

        # Build result incrementally
        result.add_error("missing_method", "Missing execute() method")
        result.add_warning("deprecated_method", "Using deprecated pattern")
        ```

    See Also:
        - ProtocolValidationError: Error representation
        - ProtocolValidator: Validation interface
    """

    is_valid: bool
    protocol_name: str
    implementation_name: str
    errors: list[ProtocolValidationError]
    warnings: list[ProtocolValidationError]

    def add_error(
        self,
        error_type: str,
        message: str,
        context: dict[str, ContextValue] | None = None,
        severity: str | None = None,
    ) -> None: ...

    def add_warning(
        self,
        error_type: str,
        message: str,
        context: dict[str, ContextValue] | None = None,
    ) -> None: ...

    async def get_summary(self) -> str: ...


@runtime_checkable
class ProtocolValidator(Protocol):
    """
    Protocol for protocol compliance validation functionality.

    Provides the interface for validating whether implementations
    satisfy protocol requirements, with configurable strict mode
    for additional validation rigor.

    Attributes:
        strict_mode: Whether to enforce strict validation rules

    Example:
        ```python
        validator: ProtocolValidator = get_validator()
        validator.strict_mode = True

        result = await validator.validate_implementation(my_impl, ProtocolNode)

        if result.is_valid:
            print("Implementation fully satisfies protocol")
        else:
            for error in result.errors:
                print(f"Violation: {error.message}")
        ```

    See Also:
        - ProtocolValidationResult: Validation outcome
        - ProtocolValidationDecorator: Decorator-based validation
    """

    strict_mode: bool

    async def validate_implementation(
        self, implementation: T, protocol: type[P]
    ) -> "ProtocolValidationResult": ...


@runtime_checkable
class ProtocolValidationDecorator(Protocol):
    """
    Protocol for decorator-based protocol validation functionality.

    Provides the interface for applying protocol validation as
    decorators on classes, enabling declarative validation with
    configurable strictness at the decorator or call level.

    Example:
        ```python
        decorator: ProtocolValidationDecorator = get_validation_decorator()

        # Apply as decorator
        @decorator.validation_decorator(ProtocolNode)
        class MyNode:
            async def execute(self, input_data): ...

        # Or validate explicitly
        result = await decorator.validate_protocol_implementation(
            my_impl, ProtocolNode, strict=True
        )
        ```

    See Also:
        - ProtocolValidator: Core validation interface
        - ProtocolValidationResult: Validation outcome
    """

    async def validate_protocol_implementation(
        self, implementation: T, protocol: type[P], strict: bool | None = None
    ) -> "ProtocolValidationResult": ...

    def validation_decorator(self, protocol: type[P]) -> object: ...
