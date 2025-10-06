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
    """Protocol for validation error objects."""

    error_type: str
    message: str
    context: dict[str, ContextValue]
    severity: str

    def __str__(self) -> str: ...


@runtime_checkable
class ProtocolValidationResult(Protocol):
    """Protocol for validation result objects."""

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
        severity: str = "error",
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
    """Protocol for protocol validation functionality."""

    strict_mode: bool

    async def validate_implementation(
        self, implementation: T, protocol: type[P]
    ) -> "ProtocolValidationResult": ...


@runtime_checkable
class ProtocolValidationDecorator(Protocol):
    """Protocol for validation decorator functionality."""

    async def validate_protocol_implementation(
        self, implementation: T, protocol: type[P], strict: bool = True
    ) -> "ProtocolValidationResult": ...

    def validation_decorator(self, protocol: type[P]) -> object: ...
