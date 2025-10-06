"""
Protocol definition for error sanitization and sensitive data masking.

This protocol defines the interface for sanitizing error messages and
removing sensitive information from logs and error reports following
ONEX security standards.
"""

from typing import Any, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue


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

    def sanitize_message(self, message: str) -> str: ...

    def sanitize_exception(self, exception: Exception) -> Exception: ...

    def sanitize_dict(
        self, data: dict[str, ContextValue]
    ) -> dict[str, ContextValue]: ...

    def sanitize_list(self, data: list["ContextValue"]) -> list["ContextValue"]: ...

    def sanitize_file_path(self, path: str) -> str: ...

    async def get_cache_info(self) -> dict[str, ContextValue]: ...


@runtime_checkable
class ProtocolErrorSanitizerFactory(Protocol):
    """
    Protocol for error sanitizer factory implementations.

    Factories create and configure error sanitizers with different
    security levels and pattern sets.
    """

    async def create_default(self) -> ProtocolErrorSanitizer: ...
