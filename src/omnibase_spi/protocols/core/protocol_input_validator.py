"""
Protocol for Input Validation.

Defines interfaces for standardized input validation, sanitization,
and security-focused data validation across ONEX services.
"""

from typing import TYPE_CHECKING, Optional, Protocol, Union, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.core_types import (
        ContextValue,
        ProtocolValidationResult,
        ValidationLevel,
        ValidationMode,
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
            def validate_input(self, value, rules, level):
                result = ValidationResult(is_valid=True, errors=[], warnings=[])

                for rule in rules:
                    if rule == "max_length" and len(str(value)) > 1000:
                        result.is_valid = False
                        result.errors.append("Input exceeds maximum length")

                return result

        # Usage in application code
        validator: ProtocolInputValidator = InputValidatorImpl()

        result = validator.validate_input(
            value=user_input,
            rules=["required", "max_length:255", "no_sql_injection"],
            validation_level="standard"
        )

        if not result.is_valid:
            raise ValidationError(result.errors)
        ```
    """

    def validate_input(
        self,
        value: "ContextValue",
        rules: list[str],
        validation_level: "ValidationLevel" = "STANDARD",
    ) -> "ProtocolValidationResult":
        """
        Validate input value against specified rules.

        Args:
            value: Value to validate
            rules: List of validation rule names
            validation_level: Thoroughness of validation

        Returns:
            Validation result with errors and warnings

        Note:
            Validation rules include type checking, size limits,
            format validation, and security pattern detection.
        """
        ...

    def validate_string(
        self,
        value: str,
        min_length: Optional[int],
        max_length: Optional[int],
        pattern: Optional[str],
        allow_empty: bool,
    ) -> "ProtocolValidationResult":
        """
        Validate string with comprehensive checks.

        Args:
            value: String to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            pattern: Regex pattern for format validation
            allow_empty: Whether empty strings are allowed

        Returns:
            Validation result with detailed feedback

        Note:
            Includes checks for SQL injection, XSS, path traversal,
            and other common security vulnerabilities.
        """
        ...

    def validate_numeric(
        self,
        value: Union[float, int],
        min_value: Optional[float],
        max_value: Optional[float],
        allow_negative: bool,
        precision: Optional[int],
    ) -> "ProtocolValidationResult":
        """
        Validate numeric value with range and precision checks.

        Args:
            value: Numeric value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_negative: Whether negative values are allowed
            precision: Maximum decimal places for floats

        Returns:
            Validation result with range and precision feedback

        Note:
            Prevents numeric overflow, underflow, and precision issues
            that could cause application vulnerabilities.
        """
        ...

    def validate_collection(
        self,
        value: Union[list[object], dict[str, object]],
        max_size: Optional[int],
        item_rules: Optional[list[str]],
        unique_items: bool,
    ) -> "ProtocolValidationResult":
        """
        Validate collection (list or dict) with size and item checks.

        Args:
            value: Collection to validate
            max_size: Maximum number of items allowed
            item_rules: Validation rules to apply to each item
            unique_items: Whether items must be unique

        Returns:
            Validation result with collection and item feedback

        Note:
            Prevents DoS attacks through oversized collections
            and validates collection structure and contents.
        """
        ...

    def validate_email(
        self,
        email: str,
        check_mx: bool,
        allow_international: bool,
    ) -> "ProtocolValidationResult":
        """
        Validate email address format and optionally domain.

        Args:
            email: Email address to validate
            check_mx: Whether to check MX record existence
            allow_international: Whether to allow international domains

        Returns:
            Validation result with email-specific feedback

        Note:
            Validates email format against RFC standards and
            optionally verifies domain existence for deliverability.
        """
        ...

    def validate_url(
        self,
        url: str,
        allowed_schemes: Optional[list[str]],
        allow_private_ips: bool,
        max_length: int,
    ) -> "ProtocolValidationResult":
        """
        Validate URL format and security characteristics.

        Args:
            url: URL to validate
            allowed_schemes: List of allowed URL schemes (http, https, etc.)
            allow_private_ips: Whether private IP addresses are allowed
            max_length: Maximum URL length

        Returns:
            Validation result with URL-specific feedback

        Note:
            Prevents SSRF attacks by validating URL schemes and
            blocking access to private network resources.
        """
        ...

    def sanitize_input(
        self,
        value: str,
        remove_html: bool,
        escape_special_chars: bool,
        normalize_whitespace: bool,
    ) -> str:
        """
        Sanitize input string for safe usage.

        Args:
            value: String to sanitize
            remove_html: Whether to strip HTML tags
            escape_special_chars: Whether to escape special characters
            normalize_whitespace: Whether to normalize whitespace

        Returns:
            Sanitized string safe for processing

        Note:
            Removes or escapes potentially dangerous content
            while preserving legitimate data for application use.
        """
        ...

    def validate_batch(
        self,
        inputs: list[dict[str, object]],
        validation_mode: "ValidationMode" = "strict",
    ) -> list["ProtocolValidationResult"]:
        """
        Validate multiple inputs in batch for performance.

        Args:
            inputs: List of input dictionaries with validation rules
            validation_mode: Validation strictness level

        Returns:
            List of validation results corresponding to inputs

        Note:
            Batch validation reduces overhead for bulk operations
            while maintaining individual validation feedback.
        """
        ...

    def add_custom_rule(
        self,
        rule_name: str,
        validator_function: object,
        error_message: str,
    ) -> bool:
        """
        Add custom validation rule.

        Args:
            rule_name: Name for the custom rule
            validator_function: Function to perform validation
            error_message: Error message for validation failures

        Returns:
            True if rule was added successfully

        Note:
            Enables domain-specific validation rules while
            maintaining consistent validation interface.
        """
        ...

    def check_security_patterns(
        self,
        value: str,
        check_sql_injection: bool,
        check_xss: bool,
        check_path_traversal: bool,
        check_command_injection: bool,
    ) -> "ProtocolValidationResult":
        """
        Check input for common security attack patterns.

        Args:
            value: String to check for security threats
            check_sql_injection: Whether to check for SQL injection
            check_xss: Whether to check for XSS attacks
            check_path_traversal: Whether to check for path traversal
            check_command_injection: Whether to check for command injection

        Returns:
            Validation result with security threat analysis

        Note:
            Provides comprehensive security pattern detection
            to prevent common web application vulnerabilities.
        """
        ...

    def get_validation_statistics(
        self,
        time_window_hours: int,
    ) -> dict[str, object]:
        """
        Get validation statistics for monitoring.

        Args:
            time_window_hours: Hours of statistics to include

        Returns:
            Validation statistics including failure rates and patterns

        Note:
            Provides operational visibility into validation patterns
            and potential security threats for monitoring systems.
        """
        ...

    def validate_with_rate_limit(
        self,
        value: str,
        caller_id: str,
        max_requests_per_minute: int,
        validation_type: str,
    ) -> "ProtocolValidationResult":
        """
        Validate input with rate limiting to prevent validation DoS attacks.

        Args:
            value: Input value to validate
            caller_id: Unique identifier for the caller (IP, user ID, service ID)
            max_requests_per_minute: Maximum validation requests per minute for this caller
            validation_type: Type of validation being performed (for separate rate limits)

        Returns:
            Validation result with rate limiting status

        Raises:
            RateLimitExceedException: When caller exceeds rate limit

        Note:
            Prevents validation DoS attacks by limiting validation requests
            per caller. Different validation types can have separate limits.
        """
        ...

    def get_rate_limit_status(
        self,
        caller_id: str,
        validation_type: str,
    ) -> dict[str, object]:
        """
        Get current rate limit status for a caller.

        Args:
            caller_id: Unique identifier for the caller
            validation_type: Type of validation to check rate limit for

        Returns:
            Rate limit status including remaining requests, reset time, etc.

        Note:
            Allows callers to check their rate limit status proactively
            and implement appropriate backoff strategies.
        """
        ...
