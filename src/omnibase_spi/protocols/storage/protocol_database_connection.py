"""
Protocol for Database Connection abstraction.

Provides a clean interface for database operations with proper fallback
strategies and connection management.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_storage_types import (
    ProtocolConnectionInfo,
    ProtocolLockResult,
    ProtocolQueryResult,
    ProtocolServiceHealth,
    ProtocolTransactionResult,
)

# Type alias for database parameter values
DbParamType = str | int | float | bool | bytes | None


@runtime_checkable
class ProtocolDatabaseConnection(Protocol):
    """
    Protocol for database connection management.

    Abstracts database operations from specific implementations like asyncpg,
    aiomysql, or in-memory fallbacks. Provides unified interface for database
    connectivity, query execution, transaction management, and health monitoring.

    Example:
        @runtime_checkable
        class PostgreSQLConnection(Protocol):
            @property
            def connection_string(self) -> str: ...
            @property
            def connection(self) -> object | None: ...

            async def connect(self) -> bool: ...
            async def disconnect(self, timeout_seconds: float = 30.0) -> None: ...
            async def execute_query(
                self, query: str, parameters: tuple[DbParamType, ...] | None
            ) -> ProtocolQueryResult: ...
    """

    async def connect(self) -> bool:
        """
        Establish connection to the database.

        Returns:
            bool: True if connection successful, False otherwise
        """
        ...

    async def disconnect(self, timeout_seconds: float = 30.0) -> None:
        """
        Close database connection and clean up resources.

        Args:
            timeout_seconds: Maximum time to wait for disconnect to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If disconnect does not complete within the specified timeout.
        """
        ...

    async def execute_query(
        self,
        query: str,
        parameters: tuple[DbParamType, ...] | None = None,
    ) -> ProtocolQueryResult:
        """
        Execute a SELECT query and return results.

        Args:
            query: SQL query string to execute
            parameters: Optional query parameters for parameterized queries

        Returns:
            ProtocolQueryResult: Query execution results with row data, execution metrics,
                               and success status
        """
        ...

    async def execute_command(
        self,
        command: str,
        parameters: tuple[DbParamType, ...] | None = None,
    ) -> ProtocolQueryResult:
        """
        Execute an INSERT, UPDATE, or DELETE command.

        Args:
            command: SQL command string to execute
            parameters: Optional command parameters for parameterized commands

        Returns:
            ProtocolQueryResult: Command execution results with affected rows count
                               and execution metrics
        """
        ...

    async def execute_transaction(
        self,
        commands: list[tuple[str, tuple[DbParamType, ...] | None]],
    ) -> ProtocolTransactionResult:
        """
        Execute multiple commands in a transaction.

        Args:
            commands: List of (command, parameters) tuples to execute transactionally

        Returns:
            ProtocolTransactionResult: Transaction execution results with commit/rollback
                                       status and execution metrics
        """
        ...

    async def acquire_lock(
        self,
        lock_name: str,
        timeout_seconds: int | None = None,
    ) -> ProtocolLockResult:
        """
        Acquire a named advisory lock.

        Args:
            lock_name: Name of the lock to acquire
            timeout_seconds: Maximum time to wait for lock acquisition

        Returns:
            ProtocolLockResult: Lock acquisition result with lock token and expiration
        """
        ...

    async def release_lock(self, lock_token: str) -> bool:
        """
        Release an advisory lock.

        Args:
            lock_token: Token returned by acquire_lock identifying the lock to release

        Returns:
            bool: True if released successfully, False otherwise
        """
        ...

    async def health_check(self) -> ProtocolServiceHealth:
        """
        Check database health and connection status.

        Returns:
            ProtocolServiceHealth: Comprehensive health information including connection
                                  status, response times, and system metrics
        """
        ...

    async def get_connection_info(self) -> ProtocolConnectionInfo:
        """
        Get connection information and statistics.

        Returns:
            ProtocolConnectionInfo: Detailed connection information including pool stats,
                                  connection metrics, and configuration details
        """
        ...
