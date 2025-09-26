"""
Typed configuration protocols for HTTP and Kafka clients.

Provides strongly-typed configuration contracts to replace generic
dict returns with specific, validated configuration structures.
"""

from typing import Optional, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolHttpClientConfig(Protocol):
    """
    Protocol for HTTP client configuration parameters.

    Defines typed configuration structure for HTTP clients with
    connection pooling, security, retry logic, and performance settings.

    Example:
        ```python
        config: ProtocolHttpClientConfig = get_http_config()

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
    ssl_cert_path: Optional[str]
    ssl_key_path: Optional[str]
    user_agent: str
    default_headers: dict[str, ContextValue]
    proxy_url: Optional[str]
    proxy_auth: Optional[str]
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

    auth_type: str  # "bearer", "basic", "oauth2", "api_key", "none"
    bearer_token: Optional[str]
    basic_username: Optional[str]
    basic_password: Optional[str]
    api_key_header: Optional[str]
    api_key_value: Optional[str]
    oauth2_client_id: Optional[str]
    oauth2_client_secret: Optional[str]
    oauth2_token_url: Optional[str]
    oauth2_scope: Optional[str]
    refresh_token_automatically: bool
    token_expiry_buffer_seconds: int


@runtime_checkable
class ProtocolKafkaClientConfig(Protocol):
    """
    Protocol for Kafka client configuration parameters.

    Defines typed configuration structure for Kafka clients with
    connection settings, security, performance tuning, and reliability.

    Example:
        ```python
        config: ProtocolKafkaClientConfig = get_kafka_config()

        print(f"Brokers: {config.bootstrap_servers}")
        print(f"Security: {config.security_protocol}")
        print(f"Batch size: {config.batch_size}")
        print(f"Compression: {config.compression_type}")
        ```
    """

    bootstrap_servers: list[str]
    client_id: str
    security_protocol: str  # "PLAINTEXT", "SSL", "SASL_PLAINTEXT", "SASL_SSL"
    ssl_ca_location: Optional[str]
    ssl_certificate_location: Optional[str]
    ssl_key_location: Optional[str]
    ssl_key_password: Optional[str]
    sasl_mechanism: Optional[
        str
    ]  # "PLAIN", "SCRAM-SHA-256", "SCRAM-SHA-512", "OAUTHBEARER"
    sasl_username: Optional[str]
    sasl_password: Optional[str]
    request_timeout_ms: int
    retry_backoff_ms: int
    max_retry_attempts: int
    session_timeout_ms: int
    heartbeat_interval_ms: int
    max_poll_interval_ms: int


@runtime_checkable
class ProtocolKafkaProducerConfig(Protocol):
    """
    Protocol for Kafka producer-specific configuration parameters.

    Defines typed configuration for producer performance, reliability,
    and delivery semantics including batching and compression settings.
    """

    acks: str  # "0", "1", "all"
    batch_size: int
    linger_ms: int
    buffer_memory: int
    compression_type: str  # "none", "gzip", "snappy", "lz4", "zstd"
    max_in_flight_requests_per_connection: int
    retries: int
    delivery_timeout_ms: int
    enable_idempotence: bool
    transactional_id: Optional[str]
    max_request_size: int
    send_buffer_bytes: int
    receive_buffer_bytes: int


@runtime_checkable
class ProtocolKafkaConsumerConfig(Protocol):
    """
    Protocol for Kafka consumer-specific configuration parameters.

    Defines typed configuration for consumer group management, offset handling,
    and message consumption patterns including auto-commit and fetch settings.
    """

    group_id: str
    auto_offset_reset: str  # "earliest", "latest", "none"
    enable_auto_commit: bool
    auto_commit_interval_ms: int
    max_poll_records: int
    fetch_min_bytes: int
    fetch_max_wait_ms: int
    max_partition_fetch_bytes: int
    check_crcs: bool
    isolation_level: str  # "read_uncommitted", "read_committed"
    exclude_internal_topics: bool
    partition_assignment_strategy: (
        str  # "range", "roundrobin", "sticky", "cooperative-sticky"
    )
    allow_auto_create_topics: bool


@runtime_checkable
class ProtocolClientConfigProvider(Protocol):
    """
    Protocol for client configuration provider.

    Provides access to typed configuration objects for HTTP and Kafka clients
    with support for environment-based overrides and configuration validation.

    Example:
        ```python
        provider: ProtocolClientConfigProvider = get_config_provider()

        http_config = provider.get_http_client_config("api_client")
        kafka_config = provider.get_kafka_client_config("event_processor")

        # Validate configurations
        await provider.validate_configurations()
        ```
    """

    def get_http_client_config(self, client_name: str) -> ProtocolHttpClientConfig:
        """
        Get HTTP client configuration for named client.

        Args:
            client_name: Name of the HTTP client configuration

        Returns:
            HTTP client configuration protocol implementation

        Raises:
            OnexError: If configuration is not found or invalid
        """
        ...

    def get_http_auth_config(self, auth_name: str) -> ProtocolHttpAuthConfig:
        """
        Get HTTP authentication configuration for named auth scheme.

        Args:
            auth_name: Name of the authentication configuration

        Returns:
            HTTP auth configuration protocol implementation

        Raises:
            OnexError: If auth configuration is not found or invalid
        """
        ...

    def get_kafka_client_config(self, client_name: str) -> ProtocolKafkaClientConfig:
        """
        Get Kafka client configuration for named client.

        Args:
            client_name: Name of the Kafka client configuration

        Returns:
            Kafka client configuration protocol implementation

        Raises:
            OnexError: If configuration is not found or invalid
        """
        ...

    def get_kafka_producer_config(
        self, producer_name: str
    ) -> ProtocolKafkaProducerConfig:
        """
        Get Kafka producer configuration for named producer.

        Args:
            producer_name: Name of the producer configuration

        Returns:
            Kafka producer configuration protocol implementation

        Raises:
            OnexError: If configuration is not found or invalid
        """
        ...

    def get_kafka_consumer_config(
        self, consumer_name: str
    ) -> ProtocolKafkaConsumerConfig:
        """
        Get Kafka consumer configuration for named consumer.

        Args:
            consumer_name: Name of the consumer configuration

        Returns:
            Kafka consumer configuration protocol implementation

        Raises:
            OnexError: If configuration is not found or invalid
        """
        ...

    async def validate_configurations(self) -> list[str]:
        """
        Validate all loaded configurations.

        Checks configuration completeness, validates connectivity,
        and verifies security settings.

        Returns:
            List of validation warnings or empty list if all valid

        Raises:
            OnexError: If critical configuration errors are found
        """
        ...

    async def reload_configurations(self) -> None:
        """
        Reload configurations from source.

        Refreshes configuration data from environment variables,
        config files, or external configuration services.

        Raises:
            OnexError: If configuration reload fails
        """
        ...

    def get_configuration_summary(self) -> dict[str, dict[str, str | int | bool]]:
        """
        Get summary of all loaded configurations.

        Returns non-sensitive configuration information for debugging
        and monitoring purposes.

        Returns:
            Dictionary with configuration summaries (sensitive data masked)
        """
        ...
