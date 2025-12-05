"""
Protocol for Connection Management and Lifecycle Control.

Defines interfaces for connection establishment, monitoring, health checks,
and recovery strategies across all ONEX services with consistent patterns
and resilient connection handling.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralConnectionState,
    ProtocolConnectionConfig,
    ProtocolConnectionStatus,
    ProtocolRetryConfig,
)


@runtime_checkable
class ProtocolConnectionManageable(Protocol):
    """
    Protocol for comprehensive connection management across ONEX services.

    Provides consistent connection lifecycle management, health monitoring,
    reconnection strategies, and resilient connection handling for distributed
    system reliability and fault tolerance.

    Key Features:
        - Connection lifecycle management (connect, disconnect, close)
        - Real-time connection status monitoring and health checks
        - Automatic reconnection with configurable retry strategies
        - Connection pool management and resource optimization
        - Graceful degradation and circuit breaker patterns
        - Connection metrics collection and performance monitoring
        - Event-driven connection state notifications
        - SSL/TLS security configuration and validation

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        service: "ConnectionManageable" = get_connection_manageable()

        # Usage demonstrates protocol interface without implementation details
        # All operations work through the protocol contract
        # Implementation details are abstracted away from the interface

        connection_mgr: "ProtocolConnectionManageable" = DatabaseConnectionManager()

        # Establish connection with retry
        success = await connection_mgr.establish_connection()
        if not success:
            await connection_mgr.reconnect_with_strategy(retry_config)

        # Monitor connection health
        if await connection_mgr.perform_health_check():
            # Connection is healthy, proceed with operations
            pass
        else:
            # Connection unhealthy, trigger recovery
            await connection_mgr.recover_connection()
        ```

    Connection States:
        - disconnected: No active connection established
        - connecting: In process of establishing connection
        - connected: Active connection ready for operations
        - reconnecting: Attempting to restore lost connection
        - failed: Connection failed and requires intervention
        - closing: Gracefully shutting down connection

    Reconnection Strategies:
        - immediate: Attempt reconnection without delay
        - exponential_backoff: Exponentially increasing delays between attempts
        - linear_backoff: Linear delay increases for predictable retry timing
        - circuit_breaker: Temporary connection suspension after failure threshold
        - manual: Require explicit reconnection request (no auto-retry)

    Health Check Levels:
        - ping: Basic connectivity test (fastest)
        - shallow: Basic query or lightweight operation
        - deep: Comprehensive connection validation and feature check
        - diagnostic: Full connection diagnostics with performance metrics
    """

    connection_id: str
    config: "ProtocolConnectionConfig"
    status: "ProtocolConnectionStatus"
    can_reconnect: bool
    auto_reconnect_enabled: bool

    async def establish_connection(self) -> bool: ...

    async def close_connection(self, timeout_seconds: float = 30.0) -> bool:
        """Close the connection and release resources.

        Args:
            timeout_seconds: Maximum time to wait for close to complete.
                Defaults to 30.0 seconds.

        Returns:
            True if close succeeded, False otherwise.

        Raises:
            TimeoutError: If close does not complete within the specified timeout.
        """
        ...

    async def disconnect(self, timeout_seconds: float = 30.0) -> bool:
        """Disconnect from the remote service.

        Args:
            timeout_seconds: Maximum time to wait for disconnect to complete.
                Defaults to 30.0 seconds.

        Returns:
            True if disconnect succeeded, False otherwise.

        Raises:
            TimeoutError: If disconnect does not complete within the specified timeout.
        """
        ...

    async def reconnect_immediate(self) -> bool: ...

    async def reconnect_with_strategy(
        self, retry_config: "ProtocolRetryConfig"
    ) -> bool: ...

    async def recover_connection(self) -> bool: ...

    async def perform_health_check(self) -> bool: ...

    async def perform_deep_health_check(self) -> dict[str, "ContextValue"]: ...

    async def get_connection_state(self) -> "LiteralConnectionState": ...

    async def get_connection_status(self) -> "ProtocolConnectionStatus": ...

    async def get_connection_metrics(self) -> dict[str, "ContextValue"]: ...

    async def update_connection_config(
        self, new_config: "ProtocolConnectionConfig"
    ) -> bool: ...

    async def enable_auto_reconnect(self) -> bool: ...

    async def disable_auto_reconnect(self) -> bool: ...

    async def is_connected(self) -> bool: ...

    async def is_connecting(self) -> bool: ...

    def can_recover(self) -> bool: ...

    async def get_last_error(self) -> str | None: ...

    async def get_connection_uptime(self) -> int: ...

    async def get_idle_time(self) -> int: ...

    async def reset_error_count(self) -> bool: ...

    async def set_connection_timeout(self, timeout_ms: int) -> bool: ...

    async def get_connection_pool_stats(self) -> dict[str, "ContextValue"] | None: ...

    async def validate_connection_config(
        self, config: "ProtocolConnectionConfig"
    ) -> bool: ...

    async def test_connection_config(
        self, config: "ProtocolConnectionConfig"
    ) -> dict[str, "ContextValue"]: ...

    async def get_supported_features(self) -> list[str]: ...

    def is_feature_available(self, feature_name: str) -> bool: ...
