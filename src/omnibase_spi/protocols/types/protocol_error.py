"""
ONEX error protocol types.

Domain: ONEX error objects and error handling
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolError(Protocol):
    """
    Protocol for ONEX error objects.

    Provides standardized error representation across ONEX services with
    categorization, context, and serialization support. Used for consistent
    error handling and reporting throughout distributed systems.

    Key Features:
        - Error code classification for programmatic handling
        - Human-readable error messages for user feedback
        - Error categorization (validation/execution/configuration)
        - Optional context for debugging and diagnostics
        - Dictionary serialization for transmission and logging

    Error Categories:
        - validation: Input validation failures, schema violations
        - execution: Runtime errors, processing failures
        - configuration: Configuration errors, initialization failures

    Usage:
        error = create_onex_error(
            error_code="VALIDATION_FAILED",
            error_message="Invalid workflow configuration",
            error_category="validation",
            context={"field": "timeout", "value": -1}
        )

        # Programmatic error handling
        if error.error_code == "VALIDATION_FAILED":
            handle_validation_error(error)

        # Logging and serialization
        logger.error(f"Error: {error.error_message}", extra=error.to_dict())
    """

    @property
    def error_code(self) -> str:
        """
        Get error code for programmatic error handling.

        Returns:
            Error code string (e.g., 'VALIDATION_FAILED', 'TIMEOUT_EXCEEDED')
        """
        ...

    @property
    def error_message(self) -> str:
        """
        Get human-readable error message.

        Returns:
            Descriptive error message for user feedback and logging
        """
        ...

    @property
    def error_category(self) -> str:
        """
        Get error category for classification.

        Returns:
            Error category ('validation', 'execution', 'configuration')
        """
        ...

    @property
    def context(self) -> dict[str, object] | None:
        """
        Get error context for debugging.

        Returns:
            Optional dictionary with additional debug information,
            field values, stack traces, or diagnostic data
        """
        ...

    def to_dict(self) -> dict[str, object]:
        """
        Serialize error to dictionary for transmission and logging.

        Returns:
            Dictionary containing error_code, error_message, error_category,
            and context fields
        """
        ...
