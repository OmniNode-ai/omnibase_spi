"""
Pure SPI Protocol definitions for validation utilities.

This module contains only Protocol definitions for validation interfaces,
following SPI purity principles. Concrete implementations have been moved
to the utils/omnibase_spi_validation package.
"""

from typing import Any, Dict, List, Optional, Protocol


class ProtocolValidationError(Protocol):
    """Protocol for validation error objects."""

    error_type: str
    message: str
    context: Dict[str, Any]
    severity: str

    def __str__(self) -> str:
        """Return string representation of the error."""
        ...


class ProtocolValidationResult(Protocol):
    """Protocol for validation result objects."""

    is_valid: bool
    protocol_name: str
    implementation_name: str
    errors: List[ProtocolValidationError]
    warnings: List[ProtocolValidationError]

    def add_error(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "error",
    ) -> None:
        """Add a validation error."""
        ...

    def add_warning(
        self, error_type: str, message: str, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a validation warning."""
        ...

    def get_summary(self) -> str:
        """Get a summary of validation results."""
        ...


class ProtocolValidator(Protocol):
    """Protocol for protocol validation functionality."""

    strict_mode: bool

    def validate_implementation(
        self, implementation: Any, protocol: Any
    ) -> ProtocolValidationResult:
        """
        Validate an implementation against a protocol.

        Args:
            implementation: The implementation instance to validate
            protocol: The protocol class to validate against

        Returns:
            ProtocolValidationResult containing validation errors and warnings
        """
        ...


class ProtocolValidationDecorator(Protocol):
    """Protocol for validation decorator functionality."""

    def validate_protocol_implementation(
        self, implementation: Any, protocol: Any, strict: bool = True
    ) -> ProtocolValidationResult:
        """Validate protocol implementation."""
        ...

    def validation_decorator(self, protocol: Any) -> Any:
        """Decorator for automatic protocol validation."""
        ...


# Type aliases for backward compatibility
ValidationError = ProtocolValidationError
ValidationResult = ProtocolValidationResult
