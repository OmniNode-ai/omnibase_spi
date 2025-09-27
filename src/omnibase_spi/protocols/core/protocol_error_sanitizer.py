# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-01-15T18:45:00.000000'
# description: "Protocol" definition for error sanitization and sensitive data masking
# entrypoint: python://protocol_error_sanitizer
# hash: auto-generated
# last_modified_at: '2025-01-15T18:45:00.000000+00:00'
# lifecycle: active
# meta_type: node
# metadata_version: 0.1.0
# name: protocol_error_sanitizer.py
# namespace: python://omnibase_spi.protocols.core.protocol_error_sanitizer
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: auto-generated
# version: 1.0.0
# === /OmniNode:Metadata ===

"""
Protocol definition for error sanitization and sensitive data masking.

This protocol defines the interface for sanitizing error messages and
removing sensitive information from logs and error reports following
ONEX security standards.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolErrorSanitizer(Protocol):
    """
    Protocol for error message sanitization implementations.

    Error sanitizers protect sensitive information by masking or removing
    confidential data from error messages, logs, and exception details
    while preserving debugging context.

    Example:
        class MyErrorSanitizer:
            def sanitize_message(self, message: str) -> str:
                # Remove passwords, API keys, etc.
                return self._apply_sanitization_patterns(message)

            def sanitize_exception(self, exception: Exception) -> Exception:
                sanitized_message = self.sanitize_message(str(exception))
                return type(exception)(sanitized_message)
    """

    def sanitize_message(self, message: str) -> str:
        """
        Sanitize an error message by masking sensitive information.

        Args:
            message: Original error message that may contain sensitive data

        Returns:
            str: Sanitized message with sensitive data masked
        """
        ...

    def sanitize_exception(self, exception: Exception) -> Exception:
        """
        Sanitize an exception by masking sensitive information in its message.

        Args:
            exception: Original exception that may contain sensitive data

        Returns:
            Exception: New exception with sanitized message
        """
        ...

    def sanitize_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Sanitize a dictionary by masking sensitive values.

        Args:
            data: Dictionary that may contain sensitive information

        Returns:
            dict: Dictionary with sensitive values masked
        """
        ...

    def sanitize_list(self, data: list[Any]) -> list[Any]:
        """
        Sanitize a list by masking sensitive elements.

        Args:
            data: List that may contain sensitive information

        Returns:
            list: List with sensitive elements masked
        """
        ...

    def sanitize_file_path(self, path: str) -> str:
        """
        Sanitize a file path by masking sensitive directory names.

        Args:
            path: File path that may contain sensitive information

        Returns:
            str: Sanitized path with sensitive parts masked
        """
        ...

    def get_cache_info(self) -> dict[str, Any]:
        """
        Get information about sanitization cache performance.

        Returns:
            dict: Cache statistics and performance metrics
        """
        ...


@runtime_checkable
class ProtocolErrorSanitizerFactory(Protocol):
    """
    Protocol for error sanitizer factory implementations.

    Factories create and configure error sanitizers with different
    security levels and pattern sets.
    """

    async def create_default(self) -> ProtocolErrorSanitizer:
        """
        Create a default error sanitizer with standard patterns.

        Returns:
            ProtocolErrorSanitizer: Default sanitizer instance
        """
        ...

    async def create_strict(self) -> ProtocolErrorSanitizer:
        """
        Create a strict error sanitizer with comprehensive patterns.

        Returns:
            ProtocolErrorSanitizer: Strict sanitizer instance
        """
        ...

    async def create_lenient(self) -> ProtocolErrorSanitizer:
        """
        Create a lenient error sanitizer with minimal patterns.

        Returns:
            ProtocolErrorSanitizer: Lenient sanitizer instance
        """
        ...

    async def create_custom(
        self,
        *,
        mask_character: str,
        mask_length: int,
        preserve_prefixes: bool = True,
        custom_patterns: dict[str, Any] | None = None,
        skip_patterns: set[str] | None = None,
    ) -> ProtocolErrorSanitizer:
        """
        Create a custom error sanitizer with specified configuration.

        Args:
            mask_character: Character to use for masking
            mask_length: Length of mask strings
            preserve_prefixes: Whether to preserve prefixes in masked values
            custom_patterns: Additional patterns to include
            skip_patterns: Patterns to exclude from sanitization

        Returns:
            ProtocolErrorSanitizer: Custom configured sanitizer instance
        """
        ...
