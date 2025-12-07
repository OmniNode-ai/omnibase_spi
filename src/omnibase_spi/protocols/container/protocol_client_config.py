"""
Typed configuration protocols for HTTP and EventBus clients.

Provides strongly-typed configuration contracts to replace generic
dict returns with specific, validated configuration structures.

Note: EventBus protocols (formerly Kafka-specific) provide a backend-agnostic
interface that can be implemented for Kafka, RabbitMQ, Redis Streams, or other
message broker backends.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolHttpClientConfig(Protocol):
    """
    Protocol for HTTP client configuration parameters.

    Defines typed configuration structure for HTTP clients with
    connection pooling, security, retry logic, and performance settings.

    Example:
        ```python
        config: "ProtocolHttpClientConfig" = get_http_config()

        print(f"Base URL: {config.base_url}")
        print(f"Timeout: {config.timeout_seconds}s")
        print(f"Pool size: {config.connection_pool_size}")
        print(f"SSL verify: {config.ssl_verify}")
        ```
    """

    base_url: str
    timeout_seconds: int
    connect_timeout_seconds: int
    read_timeout_seconds: int
    max_retries: int
    retry_delay_seconds: int
    connection_pool_size: int
    max_connections_per_host: int
    ssl_verify: bool
    ssl_cert_path: str | None
    ssl_key_path: str | None
    user_agent: str
    default_headers: dict[str, "ContextValue"]
    proxy_url: str | None
    proxy_auth: str | None
    follow_redirects: bool
    max_redirects: int
    cookie_jar_enabled: bool
    compression_enabled: bool


@runtime_checkable
class ProtocolHttpAuthConfig(Protocol):
    """
    Protocol for HTTP authentication configuration.

    Defines typed authentication settings for HTTP clients including
    various authentication schemes and credential management.
    """

    auth_type: str
    bearer_token: str | None
    basic_username: str | None
    basic_password: str | None
    api_key_header: str | None
    api_key_value: str | None
    oauth2_client_id: str | None
    oauth2_client_secret: str | None
    oauth2_token_url: str | None
    oauth2_scope: str | None
    refresh_token_automatically: bool
    token_expiry_buffer_seconds: int


@runtime_checkable
class ProtocolEventBusClientConfig(Protocol):
    """
    Protocol for EventBus client configuration parameters.

    Defines typed configuration structure for EventBus clients with
    connection settings, security, performance tuning, and reliability.
    This backend-agnostic protocol can be implemented for Kafka, RabbitMQ,
    Redis Streams, or other message broker backends.

    Example:
        ```python
        config: "ProtocolEventBusClientConfig" = get_eventbus_config()

        print(f"Brokers: {config.bootstrap_servers}")
        print(f"Security: {config.security_protocol}")
        print(f"Batch size: {config.batch_size}")
        print(f"Compression: {config.compression_type}")
        ```
    """

    bootstrap_servers: list[str]
    client_id: str
    security_protocol: str
    ssl_ca_location: str | None
    ssl_certificate_location: str | None
    ssl_key_location: str | None
    ssl_key_password: str | None
    sasl_mechanism: str | None
    sasl_username: str | None
    sasl_password: str | None
    request_timeout_ms: int
    retry_backoff_ms: int
    max_retry_attempts: int
    session_timeout_ms: int
    heartbeat_interval_ms: int
    max_poll_interval_ms: int


@runtime_checkable
class ProtocolEventBusProducerConfig(Protocol):
    """
    Protocol for EventBus producer-specific configuration parameters.

    Defines typed configuration for producer performance, reliability,
    and delivery semantics including batching and compression settings.
    This backend-agnostic protocol can be implemented for Kafka, RabbitMQ,
    Redis Streams, or other message broker backends.
    """

    acks: str
    batch_size: int
    linger_ms: int
    buffer_memory: int
    compression_type: str
    max_in_flight_requests_per_connection: int
    retries: int
    delivery_timeout_ms: int
    enable_idempotence: bool
    transactional_id: str | None
    max_request_size: int
    send_buffer_bytes: int
    receive_buffer_bytes: int


@runtime_checkable
class ProtocolEventBusConsumerConfig(Protocol):
    """
    Protocol for EventBus consumer-specific configuration parameters.

    Defines typed configuration for consumer group management, offset handling,
    and message consumption patterns including auto-commit and fetch settings.
    This backend-agnostic protocol can be implemented for Kafka, RabbitMQ,
    Redis Streams, or other message broker backends.
    """

    group_id: str
    auto_offset_reset: str
    enable_auto_commit: bool
    auto_commit_interval_ms: int
    max_poll_records: int
    fetch_min_bytes: int
    fetch_max_wait_ms: int
    max_partition_fetch_bytes: int
    check_crcs: bool
    isolation_level: str
    exclude_internal_topics: bool
    partition_assignment_strategy: str
    allow_auto_create_topics: bool


@runtime_checkable
class ProtocolClientConfigProvider(Protocol):
    """
    Protocol for client configuration provider.

    Provides access to typed configuration objects for HTTP and EventBus clients
    with support for environment-based overrides and configuration validation.

    Example:
        ```python
        provider: "ProtocolClientConfigProvider" = get_config_provider()

        http_config = provider.get_http_client_config("api_client")
        eventbus_config = provider.get_eventbus_client_config("event_processor")

        # Validate configurations
        await provider.validate_configurations()
        ```
    """

    async def get_http_client_config(
        self, client_name: str
    ) -> ProtocolHttpClientConfig: ...

    async def get_http_auth_config(self, auth_name: str) -> ProtocolHttpAuthConfig: ...

    async def get_eventbus_client_config(
        self, client_name: str
    ) -> ProtocolEventBusClientConfig: ...

    async def get_eventbus_producer_config(
        self, producer_name: str
    ) -> ProtocolEventBusProducerConfig: ...

    async def get_eventbus_consumer_config(
        self, consumer_name: str
    ) -> ProtocolEventBusConsumerConfig: ...

    async def validate_configurations(self) -> list[str]: ...
