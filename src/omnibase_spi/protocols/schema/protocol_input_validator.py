"""
Protocol for Input Validation.

Defines interfaces for standardized input validation, sanitization,
and security-focused data validation across ONEX services.
"""

from collections.abc import Callable
from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralValidationLevel,
    LiteralValidationMode,
)
from omnibase_spi.protocols.validation.protocol_validation import (
    ProtocolValidationResult,
)


@runtime_checkable
class ProtocolInputValidator(Protocol):
    """
    Protocol for standardized input validation across ONEX services.

    Provides comprehensive input validation, sanitization, and security
    checking to prevent injection attacks and ensure data integrity.

    Key Features:
        - Multi-level validation (basic to paranoid)
        - Type-specific validation rules
        - Size and format constraints
        - Security-focused validation patterns
        - Custom validation rule support
        - Batch validation for performance

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        class InputValidatorImpl:
            async def validate_input(self, value, rules, level):
                result = ValidationResult(is_valid=True, errors=[], warnings=[])

                for rule in rules:
                    if rule == "max_length" and len(str(value)) > 1000:
                        result.is_valid = False
                        result.errors.append("Input exceeds maximum length")

                return result

        # Usage in application code
        validator: "ProtocolInputValidator" = InputValidatorImpl()

        result = validator.validate_input(
            value=user_input,
            rules=["required", "max_length:255", "no_sql_injection"],
            validation_level="standard"
        )

        if not result.is_valid:
            raise ValidationError(result.errors)
        ```
    """

    async def validate_input(
        self,
        value: "ContextValue",
        rules: list[str],
        validation_level: "LiteralValidationLevel" = "STANDARD",
    ) -> "ProtocolValidationResult": ...

    async def validate_string(
        self,
        value: str,
        min_length: int | None,
        max_length: int | None,
        pattern: str | None,
        allow_empty: bool,
    ) -> "ProtocolValidationResult": ...

    async def validate_numeric(
        self,
        value: float | int,
        min_value: float | None,
        max_value: float | None,
        allow_negative: bool,
        precision: int | None,
    ) -> "ProtocolValidationResult": ...

    async def validate_collection(
        self,
        value: list[object] | dict[str, object],
        max_size: int | None,
        item_rules: list[str] | None,
        unique_items: bool,
    ) -> "ProtocolValidationResult": ...

    async def validate_email(
        self, email: str, check_mx: bool, allow_international: bool
    ) -> "ProtocolValidationResult": ...

    async def validate_url(
        self,
        url: str,
        allowed_schemes: list[str] | None,
        allow_private_ips: bool,
        max_length: int,
    ) -> "ProtocolValidationResult": ...

    async def sanitize_input(
        self,
        value: str,
        remove_html: bool | None = None,
        escape_special_chars: bool | None = None,
        normalize_whitespace: bool | None = None,
    ) -> str: ...

    async def validate_batch(
        self,
        inputs: list[dict[str, object]],
        validation_mode: "LiteralValidationMode" = "strict",
    ) -> list["ProtocolValidationResult"]: ...

    def add_custom_rule(
        self,
        rule_name: str,
        validator_function: Callable[..., bool],
        error_message: str,
    ) -> bool: ...

    async def check_security_patterns(
        self,
        value: str,
        check_sql_injection: bool,
        check_xss: bool,
        check_path_traversal: bool,
        check_command_injection: bool,
    ) -> "ProtocolValidationResult": ...

    async def get_validation_statistics(
        self, time_window_hours: int
    ) -> dict[str, object]: ...

    async def validate_with_rate_limit(
        self,
        value: str,
        caller_id: str,
        max_requests_per_minute: int,
        validation_type: str,
    ) -> "ProtocolValidationResult": ...

    async def get_rate_limit_status(
        self, caller_id: str, validation_type: str
    ) -> dict[str, object]: ...
