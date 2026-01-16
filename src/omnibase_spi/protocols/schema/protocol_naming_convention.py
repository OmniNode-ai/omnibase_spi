"""Protocol for ONEX naming convention enforcement.

This module defines the interface for validating names against ONEX naming conventions.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolNamingConventionResult(Protocol):
    """
    Protocol for naming convention validation results.

    Captures the outcome of validating a name against ONEX naming
    conventions including validity status, any errors or warnings,
    and a suggested correction if the name is invalid.

    Attributes:
        is_valid: Whether the name conforms to naming conventions
        errors: List of critical naming convention violations
        warnings: List of non-critical naming suggestions
        suggested_name: Suggested valid name if original is invalid
    """

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    suggested_name: str | None

    def to_dict(self) -> dict[str, object]:
        """Convert the validation result to a dictionary representation.

        Serializes the result including validity status, messages,
        and suggested corrections for logging or API responses.

        Returns:
            Dictionary containing 'is_valid', 'errors', 'warnings',
            and 'suggested_name' keys with their respective values.

        Raises:
            SPIError: When serialization fails due to invalid message content.
        """
        ...


@runtime_checkable
class ProtocolNamingConvention(Protocol):
    """
    Protocol for ONEX naming convention enforcement.

    Provides validation of identifiers, file names, and other strings
    against ONEX platform naming conventions. Implementations should
    check for proper casing, allowed characters, length limits, and
    reserved word conflicts.

    Example:
        ```python
        convention: ProtocolNamingConvention = get_naming_convention()

        # Validate a node name
        result = await convention.validate_name("my_compute_node")

        if result.is_valid:
            print("Name is valid")
        else:
            for error in result.errors:
                print(f"Error: {error}")
            if result.suggested_name:
                print(f"Suggestion: {result.suggested_name}")
        ```

    See Also:
        - ProtocolNamingConventionResult: Validation result structure
        - ProtocolSchemaLoader: Schema loading with naming validation
    """

    async def validate_name(self, name: str) -> ProtocolNamingConventionResult:
        """Validate a name against ONEX naming conventions.

        Checks the provided name for compliance with platform naming
        rules including character restrictions, casing conventions,
        length limits, and reserved word conflicts. Validation errors
        are returned in the result object rather than raised as exceptions.

        Args:
            name: The name string to validate against naming conventions.

        Returns:
            Validation result containing validity status, any errors
            or warnings, and a suggested valid name if the original
            is invalid.

        Raises:
            SPIError: When validation fails due to internal processing errors.
        """
        ...
