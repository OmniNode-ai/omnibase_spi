"""Protocol for ONEX naming convention enforcement.

This module defines the interface for validating names against ONEX naming conventions.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolNamingConventionResult(Protocol):
    """Protocol for naming convention validation results."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    suggested_name: str | None

    def to_dict(self) -> dict[str, object]:
        """Serialize naming convention result to dictionary representation.

        Returns:
            Dictionary containing is_valid, errors, warnings, and suggested_name.
        """
        ...


@runtime_checkable
class ProtocolNamingConvention(Protocol):
    """
    Protocol for ONEX naming convention enforcement.

    Example:
        class MyNamingConvention:
            def validate_name(self, name: str) -> ProtocolNamingConventionResult:
                ...
    """

    async def validate_name(self, name: str) -> ProtocolNamingConventionResult: ...
