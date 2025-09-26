"""
Protocol for Connection Management and Lifecycle Control.

Defines interfaces for connection establishment, monitoring, health checks,
and recovery strategies across all ONEX services with consistent patterns
and resilient connection handling.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
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
        # Implementation example (not part of SPI)
        class DatabaseConnectionManager:
            def __init__(self, config: ProtocolConnectionConfig):
                self.connection_id = generate_connection_id()
                self.config = config
                self.status = create_initial_status()
                self._connection = None
                self._retry_count = 0

            async def establish_connection(self):
                try:
                    self.status.state = "connecting"
                    self._connection = await create_db_connection(self.config)
                    self.status.state = "connected"
                    self.status.connected_at = datetime.utcnow()
                    return True
                except Exception:
                    self.status.state = "failed"
                    self.status.error_count += 1
                    return False

            async def health_check(self):
                if not self._connection:
                    return False
                try:
                    await self._connection.ping()
                    return True
                except Exception:
                    self.status.error_count += 1
                    return False

        # Usage in application code
        connection_mgr: ProtocolConnectionManageable = DatabaseConnectionManager(config)

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

    async def establish_connection(self) -> bool:
        """
        Establish new connection using current configuration.

        Returns:
            True if connection was established successfully

        Note:
            Creates new connection based on current configuration settings.
            Updates connection status and metrics upon completion.
            Does not retry automatically - use reconnect methods for retry logic.
        """
        ...

    async def close_connection(self) -> bool:
        """
        Gracefully close current connection.

        Returns:
            True if connection was closed successfully

        Note:
            Performs graceful shutdown with proper resource cleanup.
            Updates connection status to 'closing' then 'disconnected'.
            Waits for pending operations to complete before closing.
        """
        ...

    async def disconnect(self) -> bool:
        """
        Immediately disconnect without graceful shutdown.

        Returns:
            True if disconnection completed

        Note:
            Immediate disconnection for emergency situations.
            Does not wait for pending operations to complete.
            Updates connection status to 'disconnected' immediately.
        """
        ...

    async def reconnect_immediate(self) -> bool:
        """
        Attempt immediate reconnection without delay.

        Returns:
            True if reconnection was successful

        Note:
            Performs immediate reconnection attempt for transient failures.
            Updates connection status during reconnection process.
            Does not implement retry logic - single attempt only.
        """
        ...

    async def reconnect_with_strategy(
        self, retry_config: "ProtocolRetryConfig"
    ) -> bool:
        """
        Reconnect using specified retry strategy and configuration.

        Args:
            retry_config: Retry configuration with backoff strategy and limits

        Returns:
            True if reconnection succeeded within retry limits

        Note:
            Implements configurable retry strategies (exponential, linear, fixed).
            Respects max attempts and timeout limits from retry configuration.
            Updates connection status throughout retry process.
        """
        ...

    async def recover_connection(self) -> bool:
        """
        Recover from connection failure using default recovery strategy.

        Returns:
            True if connection recovery was successful

        Note:
            Uses default retry configuration and recovery strategy.
            Suitable for automated recovery in resilient systems.
            May implement circuit breaker pattern for repeated failures.
        """
        ...

    async def perform_health_check(self) -> bool:
        """
        Perform basic connection health check.

        Returns:
            True if connection is healthy and operational

        Note:
            Performs lightweight connectivity test (ping-level check).
            Updates last activity timestamp and error count.
            Suitable for frequent health monitoring with minimal overhead.
        """
        ...

    async def perform_deep_health_check(self) -> dict[str, "ContextValue"]:
        """
        Perform comprehensive connection health assessment.

        Returns:
            Dictionary containing detailed health information and metrics

        Note:
            Comprehensive health check including performance metrics.
            Tests full connection functionality and feature availability.
            More expensive than basic health check - use sparingly.
        """
        ...

    def get_connection_state(self) -> "LiteralConnectionState":
        """
        Get current connection state.

        Returns:
            Current connection state (disconnected, connecting, connected, etc.)

        Note:
            Returns cached connection state without performing active check.
            Use perform_health_check() for up-to-date connection validation.
        """
        ...

    def get_connection_status(self) -> "ProtocolConnectionStatus":
        """
        Get comprehensive connection status information.

        Returns:
            Complete connection status with metrics and timestamps

        Note:
            Returns full status including error counts, data transfer metrics,
            and connection timing information for monitoring and diagnostics.
        """
        ...

    def get_connection_metrics(self) -> dict[str, "ContextValue"]:
        """
        Get connection performance metrics.

        Returns:
            Dictionary containing connection performance data

        Note:
            Includes metrics like bytes sent/received, error rates,
            response times, and connection pool statistics.
        """
        ...

    def update_connection_config(self, new_config: "ProtocolConnectionConfig") -> bool:
        """
        Update connection configuration.

        Args:
            new_config: New connection configuration settings

        Returns:
            True if configuration was updated successfully

        Note:
            Updates configuration for future connections.
            Does not affect current active connection.
            Requires reconnection to apply new settings.
        """
        ...

    def enable_auto_reconnect(self) -> bool:
        """
        Enable automatic reconnection on connection failure.

        Returns:
            True if auto-reconnect was enabled successfully

        Note:
            Enables background monitoring and automatic reconnection.
            Uses default retry configuration and recovery strategies.
            Connection failures will trigger automatic recovery attempts.
        """
        ...

    def disable_auto_reconnect(self) -> bool:
        """
        Disable automatic reconnection.

        Returns:
            True if auto-reconnect was disabled successfully

        Note:
            Disables background monitoring and automatic recovery.
            Connection failures will require manual reconnection.
            Existing connections remain active but won't auto-recover.
        """
        ...

    def is_connected(self) -> bool:
        """
        Check if connection is currently active and ready.

        Returns:
            True if connection is in 'connected' state

        Note:
            Quick check of connection state without performing health check.
            For actual connectivity validation, use perform_health_check().
        """
        ...

    def is_connecting(self) -> bool:
        """
        Check if connection establishment is in progress.

        Returns:
            True if connection is in 'connecting' or 'reconnecting' state

        Note:
            Indicates whether connection establishment is currently active.
            Useful for preventing concurrent connection attempts.
        """
        ...

    def can_recover(self) -> bool:
        """
        Check if connection can be recovered from current state.

        Returns:
            True if connection recovery is possible

        Note:
            Evaluates whether connection can be recovered based on
            current state, error history, and configuration.
        """
        ...

    def get_last_error(self) -> str | None:
        """
        Get description of most recent connection error.

        Returns:
            Error message from last connection failure, or None if no errors

        Note:
            Provides diagnostic information for troubleshooting
            connection issues and failure analysis.
        """
        ...

    def get_connection_uptime(self) -> int:
        """
        Get connection uptime in milliseconds.

        Returns:
            Duration connection has been active, or 0 if not connected

        Note:
            Measures time since successful connection establishment.
            Returns 0 for disconnected, failed, or connecting states.
        """
        ...

    def get_idle_time(self) -> int:
        """
        Get connection idle time in milliseconds.

        Returns:
            Duration since last connection activity

        Note:
            Measures time since last data transfer or health check.
            Useful for connection pool management and timeout policies.
        """
        ...

    def reset_error_count(self) -> bool:
        """
        Reset connection error count to zero.

        Returns:
            True if error count was reset successfully

        Note:
            Clears error count for fresh start after resolving issues.
            Useful for resetting circuit breaker states and retry logic.
        """
        ...

    def set_connection_timeout(self, timeout_ms: int) -> bool:
        """
        Set connection operation timeout.

        Args:
            timeout_ms: Timeout in milliseconds for connection operations

        Returns:
            True if timeout was set successfully

        Note:
            Applies to future connection operations and health checks.
            Does not affect operations currently in progress.
        """
        ...

    def get_connection_pool_stats(self) -> dict[str, "ContextValue"] | None:
        """
        Get connection pool statistics if applicable.

        Returns:
            Pool statistics dictionary, or None if not using connection pooling

        Note:
            Provides metrics like active connections, pool size,
            wait times, and resource utilization for pool management.
        """
        ...

    def validate_connection_config(self, config: "ProtocolConnectionConfig") -> bool:
        """
        Validate connection configuration settings.

        Args:
            config: Connection configuration to validate

        Returns:
            True if configuration is valid

        Note:
            Validates configuration parameters before applying.
            Checks host reachability, port availability, and credential validity.
        """
        ...

    async def test_connection_config(
        self, config: "ProtocolConnectionConfig"
    ) -> dict[str, "ContextValue"]:
        """
        Test connection configuration with actual connection attempt.

        Args:
            config: Connection configuration to test

        Returns:
            Test results with success status and diagnostic information

        Note:
            Performs actual connection test with provided configuration.
            Does not affect current active connection or stored configuration.
        """
        ...

    def get_supported_features(self) -> list[str]:
        """
        Get list of supported connection features.

        Returns:
            List of supported feature names

        Note:
            Returns connection-specific features like SSL/TLS support,
            compression, authentication methods, and protocol versions.
        """
        ...

    def is_feature_available(self, feature_name: str) -> bool:
        """
        Check if specific connection feature is available.

        Args:
            feature_name: Name of feature to check

        Returns:
            True if feature is available in current connection

        Note:
            Checks feature availability in active connection.
            Feature availability may vary based on server capabilities.
        """
        ...
