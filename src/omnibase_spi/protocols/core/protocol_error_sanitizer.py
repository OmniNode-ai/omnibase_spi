"""
Protocol definition for error sanitization and sensitive data masking.

This protocol defines the interface for sanitizing error messages and
removing sensitive information from logs and error reports following
ONEX security standards.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolErrorSanitizer(Protocol):
    """
    Protocol for comprehensive error message sanitization and sensitive data protection.

    Provides systematic sanitization of error messages, exceptions, structured data,
    and file paths to prevent sensitive information leakage in logs, error reports,
    and observability systems. This protocol ensures ONEX security standards are
    maintained across all error handling scenarios while preserving sufficient
    debugging context for troubleshooting.

    The sanitizer uses pattern-based detection and replacement to identify and mask
    sensitive data including credentials, API keys, tokens, PII, and internal paths.

    Example:
        ```python
        sanitizer: "ProtocolErrorSanitizer" = get_error_sanitizer()

        # Sanitize error message
        error_msg = "Connection failed: password=secret123 api_key=sk-abc123"
        clean_msg = sanitizer.sanitize_message(error_msg)
        # Returns: "Connection failed: password=<REDACTED> api_key=<REDACTED>"

        # Sanitize exception while preserving type
        try:
            authenticate(token="bearer_secret_token_xyz")
        except Exception as e:
            sanitized_exception = sanitizer.sanitize_exception(e)
            # Exception message sanitized but type preserved
            log_error(sanitized_exception)

        # Sanitize structured data
        error_context = {
            "user": "john.doe@example.com",
            "password": "mysecret",
            "api_key": "sk-1234567890",
            "request_id": "req-abc123"
        }
        clean_context = sanitizer.sanitize_dict(error_context)
        # PII and credentials masked, safe identifiers preserved

        # Sanitize file paths (remove user/internal paths)
        path = "/home/admin/secrets/credentials.yaml"
        clean_path = sanitizer.sanitize_file_path(path)
        # Returns relative or redacted path: "credentials.yaml" or "<REDACTED>/credentials.yaml"
        ```

    Key Features:
        - Pattern-based sensitive data detection and masking
        - Exception sanitization with type preservation
        - Structured data (dict/list) recursive sanitization
        - File path sanitization to prevent internal exposure
        - Configurable masking patterns and replacement tokens
        - Performance-optimized with caching support
        - Context-aware sanitization (preserve debugging value)

    Sensitive Data Patterns Detected:
        - Passwords: password=..., pwd=..., passwd=...
        - API Keys: api_key=..., apikey=..., key=...
        - Tokens: token=..., bearer=..., jwt=...
        - Secrets: secret=..., private=..., credential=...
        - PII: email addresses, phone numbers, SSN patterns
        - Internal paths: /home/..., /usr/local/..., C:\\Users\\...
        - Connection strings: Database URLs, service endpoints

    Sanitization Strategies:
        - Replacement: Replace sensitive values with <REDACTED>
        - Masking: Show partial data (first/last chars) for debugging
        - Hashing: Replace with deterministic hash for correlation
        - Truncation: Limit string length for long sensitive values
        - Removal: Complete removal of sensitive fields

    Cache Support:
        The protocol includes cache information retrieval for:
        - Monitoring sanitization performance impact
        - Pattern cache hit rates
        - Frequently sanitized patterns
        - Cache effectiveness metrics

    See Also:
        - ProtocolErrorHandler: Error handling with sanitized context
        - ProtocolLogger: Logging with automatic sanitization
        - ProtocolObservability: Observability data sanitization
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
