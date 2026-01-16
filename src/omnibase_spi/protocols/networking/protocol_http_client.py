"""
ONEX HTTP Client Protocol

This protocol defines the interface for HTTP client implementations in the ONEX architecture.
Used by EFFECT nodes that need to make external HTTP requests, particularly for webhook
and notification systems.

Security Note: Implementations must include SSRF protection and validate all target URLs.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType
    from omnibase_spi.protocols.types.protocol_event_bus_types import (
        ProtocolEventHeaders,
    )


@runtime_checkable
class ProtocolHttpResponse(Protocol):
    """
    Protocol for HTTP response data.

    Represents the response from an HTTP request with status,
    headers, and body content. Implementations must ensure
    immutability of response data.
    """

    status_code: int
    headers: "ProtocolEventHeaders"
    body: bytes


@runtime_checkable
class ProtocolHttpClient(Protocol):
    """
    Protocol for HTTP client implementations.

    This protocol defines the standard interface for making HTTP requests in ONEX.
    Implementations must provide robust error handling, timeout management,
    and security validation.

    Security Requirements:
    - Must validate URLs to prevent SSRF attacks
    - Must implement proper timeout handling
    - Must sanitize headers and request data
    - Should implement circuit breaker patterns for resilience
    """

    async def request(
        self,
        method: str,
        url: str,
        *,
        json: "JsonType | None" = None,
        headers: "ProtocolEventHeaders | None" = None,
        timeout: float | None = None,
    ) -> "ProtocolHttpResponse":
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Target URL for the request
            json: Optional JSON payload for the request body
            headers: Optional HTTP headers to include
            timeout: Request timeout in seconds (default: 10.0)

        Returns:
            ProtocolHttpResponse: Response containing status, headers, and body

        Raises:
            ModelOnexError: For any HTTP client errors, network issues, or security violations

        Security Notes:
        - URL must be validated to prevent SSRF attacks
        - Timeout must be enforced to prevent resource exhaustion
        - Headers must be sanitized to prevent injection attacks
        """
        ...

    async def health_check(self) -> bool:
        """
        Check if the HTTP client is healthy and operational.

        Returns:
            bool: True if the client is healthy, False otherwise
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """
        Clean up and close the HTTP client.

        This method should be called when the client is no longer needed
        to properly release resources and close connections.

        Args:
            timeout_seconds: Maximum time to wait for cleanup to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If cleanup does not complete within the specified timeout.
        """
        ...
