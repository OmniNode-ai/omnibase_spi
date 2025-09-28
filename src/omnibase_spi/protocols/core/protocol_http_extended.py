"""
Extended HTTP protocol definitions for advanced HTTP client operations.

Provides enhanced HTTP client protocols with support for query parameters,
form data, file uploads, streaming responses, and advanced authentication.
"""

from typing import Optional, Protocol, runtime_checkable

from omnibase_spi.protocols.core.protocol_http_client import ProtocolHttpResponse
from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolHttpRequestBuilder(Protocol):
    """
    Protocol for building complex HTTP requests with fluent interface.

    Supports query parameters, form data, file uploads, authentication,
    and other advanced HTTP features through method chaining.

    Example:
        ```python
        builder: "ProtocolHttpRequestBuilder" = get_request_builder()
        response = await builder.url("https://api.example.com/upload")             .with_query_params({"version": "2.0", "format": "json"})             .with_bearer_token("token123")             .with_file_upload({"document": file_bytes})             .post()
        ```
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
        response: "ProtocolHttpStreamingResponse" = await client.stream_get(url)

        # Stream raw content
        async for chunk in response.stream_content():
            process_chunk(chunk)

        # Stream JSON lines
        async for json_obj in response.stream_json_lines():
            process_json_object(json_obj)
        ```
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
        client: "ProtocolHttpExtendedClient" = get_extended_http_client()

        # Use request builder
        builder = client.create_request_builder()
        response = await builder.url("https://api.example.com")             .with_bearer_token("token")             .get()

        # Stream large responses
        stream_response = await client.stream_request("GET", "https://api.example.com/large-data")
        async for chunk in stream_response.stream_content():
            process(chunk)
        ```
    """

    async def create_request_builder(self) -> ProtocolHttpRequestBuilder: ...

    async def stream_request(
        self, method: str, url: str, headers: dict[str, "ContextValue"] | None = None
    ) -> ProtocolHttpStreamingResponse: ...

    async def health_check(self) -> bool: ...

    async def close(self) -> None: ...
