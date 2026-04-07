# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for database service integration.

Defines a higher-level database service interface that abstracts above
ProtocolDatabaseConnection. Where ProtocolDatabaseConnection provides
raw connection lifecycle and query execution, this protocol adds
table introspection, migration status, and structured health checks.

Adapters compose over a ProtocolDatabaseConnection instance to provide
these higher-level operations.

This protocol is a structural subtype of ProtocolExternalService.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.services.contract_database_service_types import (
        ModelDatabaseHealth,
        ModelExecuteResult,
        ModelMigrationStatus,
        ModelQueryResult,
        ModelTableInfo,
    )
    from omnibase_spi.protocols.types.protocol_service_types import (
        ProtocolServiceHealthStatus,
    )


@runtime_checkable
class ProtocolDatabaseService(Protocol):
    """Protocol for higher-level database service operations.

    Abstracts database interactions at a service level — query, execute,
    introspect tables, check migrations, and monitor health — without
    exposing raw connection details.

    This does NOT replace ProtocolDatabaseConnection, which remains the
    low-level connection protocol. Adapters implementing this protocol
    typically compose over a ProtocolDatabaseConnection instance.

    This is a structural subtype of ProtocolExternalService — any object
    satisfying this protocol also satisfies ProtocolExternalService.

    Example:
        ```python
        db: ProtocolDatabaseService = get_database_service()

        connected = await db.connect()
        if connected:
            result = await db.query("SELECT count(*) FROM events")
            info = await db.get_table_info("events")
            migrations = await db.run_migration_status()
            print(f"rows={result.row_count}, pending={migrations.pending_migrations}")

        await db.close()
        ```
    """

    # -- Lifecycle (structural subtype of ProtocolExternalService) --

    async def connect(self) -> bool:
        """Establish a connection to the database service.

        Returns:
            True if connection was established successfully, False otherwise.
        """
        ...

    async def health_check(self) -> ProtocolServiceHealthStatus:
        """Check the health of the database service connection.

        Returns:
            Health status including service ID, status, and diagnostics.
        """
        ...

    async def get_capabilities(self) -> list[str]:
        """Discover capabilities supported by this database adapter.

        Returns:
            List of capability identifiers (e.g., ``["read", "write", "ddl"]``).
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Release resources and close connections.

        Args:
            timeout_seconds: Maximum time to wait for cleanup.
        """
        ...

    # -- Domain operations --

    async def query(
        self, sql: str, params: tuple[object, ...] | None = None
    ) -> ModelQueryResult:
        """Execute a read query and return results.

        Args:
            sql: SQL query string (parameterized).
            params: Optional query parameters.

        Returns:
            Query result with columns, rows, and row count.
        """
        ...

    async def execute(
        self, sql: str, params: tuple[object, ...] | None = None
    ) -> ModelExecuteResult:
        """Execute a write statement (INSERT/UPDATE/DELETE).

        Args:
            sql: SQL statement (parameterized).
            params: Optional statement parameters.

        Returns:
            Execution result with rows affected.
        """
        ...

    async def get_table_info(self, table_name: str) -> ModelTableInfo:
        """Get metadata about a database table.

        Args:
            table_name: Name of the table to inspect.

        Returns:
            Table info including columns, row count, and size.

        Raises:
            KeyError: If table does not exist.
        """
        ...

    async def check_health(self) -> ModelDatabaseHealth:
        """Check database-specific health metrics.

        Returns:
            Database health including latency, connections, and status.
        """
        ...

    async def run_migration_status(self) -> ModelMigrationStatus:
        """Check the current migration state of the database.

        Returns:
            Migration status including current version and pending migrations.
        """
        ...
