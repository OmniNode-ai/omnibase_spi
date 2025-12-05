"""
Extended HTTP protocol definitions for advanced HTTP client operations.

Provides enhanced HTTP client protocols with support for query parameters,
form data, file uploads, streaming responses, and advanced authentication.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.networking.protocol_http_client import ProtocolHttpResponse

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolHttpRequestBuilder(Protocol):
    """
    Protocol for building complex HTTP requests with fluent interface.

    Supports query parameters, form data, file uploads, authentication,
    and other advanced HTTP features through method chaining.

    Example:
        ```python
        # Implementation example (not part of SPI)
        # All methods defined in the protocol contract must be implemented

        # Usage in application
        builder: "ProtocolHttpRequestBuilder" = get_request_builder()

        # Build complex request with multiple features
        response = await builder.url("https://api.example.com/upload") \
            .with_query_params({"version": "2.0", "format": "json"}) \
            .with_bearer_token("token123") \
            .with_file_upload({"document": file_bytes}) \
            .post()

        # Alternative: Form data submission
        response = await builder.url("https://api.example.com/submit") \
            .with_form_data({"name": "John", "email": "john@example.com"}) \
            .with_header("X-Request-ID", "req-123") \
            .post()

        # Alternative: Basic authentication
        response = await builder.url("https://api.example.com/protected") \
            .with_basic_auth("username", "password") \
            .with_timeout(30) \
            .get()
        ```

    Request Building Patterns:
        - Fluent interface for method chaining
        - Support for query parameters, form data, and JSON payloads
        - Multiple authentication methods (bearer token, basic auth)
        - File upload capabilities for multipart requests
        - Custom headers and timeout configuration
        - All HTTP methods (GET, POST, PUT, DELETE)

    Key Features:
        - Type-safe request building with validation
        - Streaming support for large file uploads
        - Authentication abstraction with multiple strategies
        - Request timeout and retry configuration
        - Header management with proper validation
        - Integration with ONEX security patterns

    Security Considerations:
        - Secure handling of authentication credentials
        - Validation of file upload types and sizes
        - Protection against header injection attacks
        - URL validation to prevent SSRF
    """

    def url(self, url: str) -> "ProtocolHttpRequestBuilder": ...

    async def with_query_params(
        self, params: dict[str, "ContextValue"]
    ) -> "ProtocolHttpRequestBuilder": ...

    def with_form_data(
        self, data: dict[str, "ContextValue"]
    ) -> "ProtocolHttpRequestBuilder": ...

    async def with_file_upload(
        self, files: dict[str, bytes]
    ) -> "ProtocolHttpRequestBuilder": ...

    def with_json(
        self, data: dict[str, str | int | float | bool]
    ) -> "ProtocolHttpRequestBuilder": ...

    def with_bearer_token(self, token: str) -> "ProtocolHttpRequestBuilder": ...

    def with_basic_auth(
        self, username: str, password: str
    ) -> "ProtocolHttpRequestBuilder": ...

    def with_header(self, name: str, value: str) -> "ProtocolHttpRequestBuilder": ...

    def with_timeout(self, timeout_seconds: int) -> "ProtocolHttpRequestBuilder": ...

    async def get(self) -> "ProtocolHttpResponse": ...

    async def post(self) -> "ProtocolHttpResponse": ...

    async def put(self) -> "ProtocolHttpResponse": ...

    async def delete(self) -> "ProtocolHttpResponse": ...


@runtime_checkable
class ProtocolHttpStreamingResponse(Protocol):
    """
    Protocol for handling streaming HTTP responses.

    Supports streaming content, JSON lines, and chunked responses
    for efficient processing of large data sets.

    Example:
        ```python
        # Implementation example (not part of SPI)
        # All methods defined in the protocol contract must be implemented

        # Usage in application
        response: "ProtocolHttpStreamingResponse" = await client.stream_get(url)

        # Stream raw binary content in chunks
        async for chunk in response.stream_content(chunk_size=8192):
            process_binary_chunk(chunk)

        # Stream JSON lines (ndjson format)
        async for json_obj in response.stream_json_lines():
            process_json_object(json_obj)

        # Stream text content line by line
        async for line in response.stream_text_lines(encoding="utf-8"):
            process_text_line(line)

        # Access response metadata
        status = response.status_code
        headers = response.headers
        source_url = response.url

        # Alternatively: Get full content for smaller responses
        if response.headers.get("content-length", 0) < 1024 * 1024:  # < 1MB
            full_content = await response.get_full_content()
            process_small_response(full_content)
        ```

    Streaming Patterns:
        - Binary content streaming with configurable chunk sizes
        - JSON lines (ndjson) streaming for structured data
        - Text line streaming for text-based responses
        - Full content access for smaller responses
        - Metadata access (status, headers, URL)

    Key Features:
        - Memory-efficient streaming for large responses
        - Support for multiple content formats (binary, JSON, text)
        - Configurable chunk sizes for optimal performance
        - Proper encoding handling for text content
        - Access to standard HTTP response metadata

    Performance Considerations:
        - Streaming prevents loading large responses into memory
        - Chunk size can be optimized based on use case
        - Backpressure support for rate-limited processing
        - Proper resource cleanup on cancellation

    Error Handling:
        - Connection errors during streaming
        - Content encoding validation
        - Chunk boundary handling
        - Stream interruption recovery
    """

    status_code: int
    headers: dict[str, "ContextValue"]
    url: str

    async def stream_content(self, chunk_size: int) -> bytes: ...

    async def stream_json_lines(self) -> dict[str, str | int | float | bool]: ...

    async def stream_text_lines(self, encoding: str) -> str: ...

    async def get_full_content(self) -> bytes: ...


@runtime_checkable
class ProtocolHttpExtendedClient(Protocol):
    """
    Protocol for extended HTTP client with advanced features.

    Provides request builders, streaming responses, connection pooling,
    and advanced configuration options for production HTTP clients.

    Example:
        ```python
        # Implementation example (not part of SPI)
        # All methods defined in the protocol contract must be implemented

        # Usage in application
        client: "ProtocolHttpExtendedClient" = get_extended_http_client()

        # Use request builder for complex requests
        builder = client.create_request_builder()
        response = await builder.url("https://api.example.com/data") \
            .with_query_params({"page": "1", "limit": "100"}) \
            .with_bearer_token("auth_token") \
            .get()

        # Stream large datasets efficiently
        stream_response = await client.stream_request(
            "GET",
            "https://api.example.com/large-dataset",
            headers={"Accept": "application/x-ndjson"}
        )

        async for json_obj in stream_response.stream_json_lines():
            process_streaming_data(json_obj)

        # Health check and lifecycle management
        is_healthy = await client.health_check()
        if not is_healthy:
            # Handle unhealthy client state
            await client.close()
            client = get_extended_http_client()  # Reinitialize
        ```

    Extended Client Patterns:
        - Request builder pattern for complex HTTP requests
        - Streaming support for large data sets and real-time responses
        - Connection pooling and resource management
        - Health monitoring and automatic recovery
        - Graceful shutdown and resource cleanup

    Key Features:
        - **Request Builder**: Fluent interface for building complex requests
        - **Streaming Responses**: Memory-efficient streaming of large responses
        - **Connection Management**: Connection pooling and keep-alive support
        - **Health Monitoring**: Built-in health checks and diagnostics
        - **Resource Lifecycle**: Proper cleanup and resource management
        - **Security Integration**: Integration with ONEX security patterns

    Production Features:
        - Automatic retry mechanisms with exponential backoff
        - Circuit breaker integration for external service resilience
        - Request/response logging and metrics collection
        - Timeout configuration at multiple levels
        - Proxy support and custom DNS resolution
        - HTTP/2 support where available

    Security Considerations:
        - Secure credential storage and handling
        - Certificate validation and pinning
        - Request signing and authentication
        - Protection against common web vulnerabilities
        - Secure default configurations

    Integration Points:
        - ONEX monitoring and observability systems
        - Circuit breaker patterns for fault tolerance
        - Distributed tracing for request correlation
        - Service discovery for dynamic endpoints
    """

    async def create_request_builder(self) -> ProtocolHttpRequestBuilder: ...

    async def stream_request(
        self, method: str, url: str, headers: dict[str, "ContextValue"] | None = None
    ) -> ProtocolHttpStreamingResponse: ...

    async def health_check(self) -> bool: ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Close the extended HTTP client and release resources.

        Args:
            timeout_seconds: Maximum time to wait for cleanup to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If cleanup does not complete within the specified timeout.
        """
        ...
