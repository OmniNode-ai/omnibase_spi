"""
Extended HTTP protocol definitions for advanced HTTP client operations.

Provides enhanced HTTP client protocols with support for query parameters,
form data, file uploads, streaming responses, and advanced authentication.
"""

from typing import Optional, Protocol, runtime_checkable

from omnibase_spi.protocols.core.protocol_http_client import ProtocolHttpResponse


@runtime_checkable
class ProtocolHttpRequestBuilder(Protocol):
    """
    Protocol for building complex HTTP requests with fluent interface.

    Supports query parameters, form data, file uploads, authentication,
    and other advanced HTTP features through method chaining.

    Example:
        ```python
        builder: ProtocolHttpRequestBuilder = get_request_builder()
        response = await builder.url("https://api.example.com/upload") \
            .with_query_params({"version": "2.0", "format": "json"}) \
            .with_bearer_token("token123") \
            .with_file_upload({"document": file_bytes}) \
            .post()
        ```
    """

    def url(self, url: str) -> "ProtocolHttpRequestBuilder":
        """
        Set the target URL for the request.

        Args:
            url: Target URL for the HTTP request

        Returns:
            Self for method chaining
        """
        ...

    def with_query_params(self, params: dict[str, str]) -> "ProtocolHttpRequestBuilder":
        """
        Add query parameters to the request URL.

        Args:
            params: Query parameters as key-value pairs

        Returns:
            Self for method chaining
        """
        ...

    def with_form_data(self, data: dict[str, str]) -> "ProtocolHttpRequestBuilder":
        """
        Set form data for the request body (application/x-www-form-urlencoded).

        Args:
            data: Form data as key-value pairs

        Returns:
            Self for method chaining
        """
        ...

    def with_file_upload(self, files: dict[str, bytes]) -> "ProtocolHttpRequestBuilder":
        """
        Add file uploads for multipart/form-data requests.

        Args:
            files: Files to upload as filename -> content mapping

        Returns:
            Self for method chaining
        """
        ...

    def with_json(
        self, data: dict[str, str | int | float | bool]
    ) -> "ProtocolHttpRequestBuilder":
        """
        Set JSON data for the request body.

        Args:
            data: JSON data to send in request body

        Returns:
            Self for method chaining
        """
        ...

    def with_bearer_token(self, token: str) -> "ProtocolHttpRequestBuilder":
        """
        Add Bearer token authentication header.

        Args:
            token: Bearer token for authentication

        Returns:
            Self for method chaining
        """
        ...

    def with_basic_auth(
        self, username: str, password: str
    ) -> "ProtocolHttpRequestBuilder":
        """
        Add Basic authentication header.

        Args:
            username: Username for basic authentication
            password: Password for basic authentication

        Returns:
            Self for method chaining
        """
        ...

    def with_header(self, name: str, value: str) -> "ProtocolHttpRequestBuilder":
        """
        Add custom header to the request.

        Args:
            name: Header name
            value: Header value

        Returns:
            Self for method chaining
        """
        ...

    def with_timeout(self, timeout_seconds: int) -> "ProtocolHttpRequestBuilder":
        """
        Set request timeout.

        Args:
            timeout_seconds: Timeout in seconds

        Returns:
            Self for method chaining
        """
        ...

    async def get(self) -> "ProtocolHttpResponse":
        """
        Execute HTTP GET request.

        Returns:
            HTTP response protocol implementation

        Raises:
            OnexError: For HTTP client errors, timeouts, or connection issues
        """
        ...

    async def post(self) -> "ProtocolHttpResponse":
        """
        Execute HTTP POST request.

        Returns:
            HTTP response protocol implementation

        Raises:
            OnexError: For HTTP client errors, timeouts, or connection issues
        """
        ...

    async def put(self) -> "ProtocolHttpResponse":
        """
        Execute HTTP PUT request.

        Returns:
            HTTP response protocol implementation

        Raises:
            OnexError: For HTTP client errors, timeouts, or connection issues
        """
        ...

    async def delete(self) -> "ProtocolHttpResponse":
        """
        Execute HTTP DELETE request.

        Returns:
            HTTP response protocol implementation

        Raises:
            OnexError: For HTTP client errors, timeouts, or connection issues
        """
        ...


@runtime_checkable
class ProtocolHttpStreamingResponse(Protocol):
    """
    Protocol for handling streaming HTTP responses.

    Supports streaming content, JSON lines, and chunked responses
    for efficient processing of large data sets.

    Example:
        ```python
        response: ProtocolHttpStreamingResponse = await client.stream_get(url)

        # Stream raw content
        async for chunk in response.stream_content():
            process_chunk(chunk)

        # Stream JSON lines
        async for json_obj in response.stream_json_lines():
            process_json_object(json_obj)
        ```
    """

    status_code: int
    headers: dict[str, str]
    url: str

    async def stream_content(self, chunk_size: int) -> bytes:
        """
        Stream response content in chunks.

        Args:
            chunk_size: Size of each chunk in bytes

        Yields:
            Content chunks as bytes

        Raises:
            OnexError: If streaming encounters errors
        """
        ...

    async def stream_json_lines(self) -> dict[str, str | int | float | bool]:
        """
        Stream JSON lines from response (newline-delimited JSON).

        Parses each line as a separate JSON object and yields the parsed data.

        Yields:
            Parsed JSON objects

        Raises:
            OnexError: If JSON parsing or streaming encounters errors
        """
        ...

    async def stream_text_lines(self, encoding: str) -> str:
        """
        Stream text lines from response.

        Args:
            encoding: Text encoding to use for decoding

        Yields:
            Text lines as strings

        Raises:
            OnexError: If text decoding or streaming encounters errors
        """
        ...

    async def get_full_content(self) -> bytes:
        """
        Read the entire response content into memory.

        Returns:
            Complete response content as bytes

        Raises:
            OnexError: If reading content encounters errors
        """
        ...


@runtime_checkable
class ProtocolHttpExtendedClient(Protocol):
    """
    Protocol for extended HTTP client with advanced features.

    Provides request builders, streaming responses, connection pooling,
    and advanced configuration options for production HTTP clients.

    Example:
        ```python
        client: ProtocolHttpExtendedClient = get_extended_http_client()

        # Use request builder
        builder = client.create_request_builder()
        response = await builder.url("https://api.example.com") \
            .with_bearer_token("token") \
            .get()

        # Stream large responses
        stream_response = await client.stream_request("GET", "https://api.example.com/large-data")
        async for chunk in stream_response.stream_content():
            process(chunk)
        ```
    """

    def create_request_builder(self) -> ProtocolHttpRequestBuilder:
        """
        Create a new request builder for complex requests.

        Returns:
            HTTP request builder instance
        """
        ...

    async def stream_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict[str, str]] = None,
    ) -> ProtocolHttpStreamingResponse:
        """
        Perform streaming HTTP request for large responses.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL for the request
            headers: Optional HTTP headers

        Returns:
            Streaming HTTP response protocol implementation

        Raises:
            OnexError: For HTTP client errors, timeouts, or connection issues
        """
        ...

    async def health_check(self) -> bool:
        """
        Check if HTTP client is healthy and ready for requests.

        Returns:
            True if client is healthy, False otherwise
        """
        ...

    async def close(self) -> None:
        """
        Close HTTP client and clean up resources.

        Should be called when client is no longer needed to properly
        close connection pools and release resources.

        Raises:
            OnexError: If cleanup encounters errors
        """
        ...
