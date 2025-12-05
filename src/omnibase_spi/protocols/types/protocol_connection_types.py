"""
Connection protocol types for ONEX SPI interfaces.

Domain: Connection configuration and status tracking.

This module contains protocol definitions for managing connections in ONEX:
- ProtocolConnectionConfig for connection configuration parameters
- ProtocolConnectionStatus for connection state and metrics tracking
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_base_types import (
    LiteralConnectionState,
    ProtocolDateTime,
)

# ==============================================================================
# Connection Configuration Protocol
# ==============================================================================


@runtime_checkable
class ProtocolConnectionConfig(Protocol):
    """
    Protocol for network connection configuration parameters.

    Defines comprehensive configuration for network connections including
    timeouts, retry behavior, SSL settings, and connection pooling.
    Used for configuring client connections to services.

    Attributes:
        host: Target hostname or IP address.
        port: Target port number.
        timeout_ms: Connection timeout in milliseconds.
        max_retries: Maximum retry attempts on failure.
        ssl_enabled: Whether to use SSL/TLS encryption.
        connection_pool_size: Number of connections to maintain.
        keep_alive_interval_ms: Interval between keep-alive probes.

    Example:
        ```python
        class DatabaseConnectionConfig:
            host: str = "db.example.com"
            port: int = 5432
            timeout_ms: int = 5000
            max_retries: int = 3
            ssl_enabled: bool = True
            connection_pool_size: int = 10
            keep_alive_interval_ms: int = 30000

            async def validate_connection_config(self) -> bool:
                return self.port > 0 and self.timeout_ms > 0

            async def is_connectable(self) -> bool:
                # Check if host is reachable
                return True

        config = DatabaseConnectionConfig()
        assert isinstance(config, ProtocolConnectionConfig)
        ```

    validate_connection_config:
        Returns:
            bool: True if connection configuration is valid.
        Raises:
            ValueError: If required fields are missing or invalid.

    is_connectable:
        Returns:
            bool: True if the host is reachable and connectable.
        Raises:
            IOError: If connection test fails.
    """

    host: str
    port: int
    timeout_ms: int
    max_retries: int
    ssl_enabled: bool
    connection_pool_size: int
    keep_alive_interval_ms: int

    async def validate_connection_config(self) -> bool: ...

    async def is_connectable(self) -> bool: ...


# ==============================================================================
# Connection Status Protocol
# ==============================================================================


@runtime_checkable
class ProtocolConnectionStatus(Protocol):
    """
    Protocol for real-time connection status and metrics tracking.

    Tracks the current state of a connection including timing, error
    counts, and throughput metrics. Used for connection monitoring
    and health checks.

    Attributes:
        state: Current connection state.
        connected_at: When the connection was established, None if not connected.
        last_activity: When last data was transferred, None if no activity.
        error_count: Cumulative error count for this connection.
        bytes_sent: Total bytes sent over this connection.
        bytes_received: Total bytes received over this connection.

    Example:
        ```python
        class ActiveConnectionStatus:
            state: LiteralConnectionState = "connected"
            connected_at: ProtocolDateTime | None = datetime_impl
            last_activity: ProtocolDateTime | None = datetime_impl
            error_count: int = 0
            bytes_sent: int = 1024000
            bytes_received: int = 2048000

            async def validate_connection_status(self) -> bool:
                return self.bytes_sent >= 0 and self.bytes_received >= 0

            async def is_connected(self) -> bool:
                return self.state == "connected"

        status = ActiveConnectionStatus()
        assert isinstance(status, ProtocolConnectionStatus)
        ```

    validate_connection_status:
        Returns:
            bool: True if connection status metrics are valid.
        Raises:
            ValueError: If status data is inconsistent.

    is_connected:
        Returns:
            bool: True if the connection is currently active.
    """

    state: LiteralConnectionState
    connected_at: "ProtocolDateTime | None"
    last_activity: "ProtocolDateTime | None"
    error_count: int
    bytes_sent: int
    bytes_received: int

    async def validate_connection_status(self) -> bool: ...

    async def is_connected(self) -> bool: ...
