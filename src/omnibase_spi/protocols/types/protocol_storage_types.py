"""
Storage types for ONEX SPI interfaces.

Domain: Storage and checkpoint management types
"""

from typing import Literal, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralHealthStatus,
    ProtocolDateTime,
    ProtocolSemVer,
)

# Storage-related literal types
LiteralStorageBackendType = Literal[
    "filesystem", "sqlite", "postgresql", "mysql", "s3", "redis", "memory"
]

LiteralCheckpointStatus = Literal[
    "creating", "active", "archived", "expired", "deleting", "failed"
]

LiteralDatabaseOperationType = Literal[
    "select", "insert", "update", "delete", "transaction", "lock"
]


# Scalar value type for database operations
@runtime_checkable
class ProtocolScalarValue(Protocol):
    """
    Protocol for scalar values in database operations.

    Provides a type-safe wrapper for primitive database values, enabling
    conversion between application types and database primitives. Used
    throughout ONEX storage systems for consistent value handling.

    Attributes:
        value: The wrapped scalar value of any type.

    Example:
        ```python
        class IntegerScalar:
            '''Integer scalar value implementation.'''

            value: int = 42

            async def to_primitive(self) -> int:
                return self.value

            async def from_primitive(self, value: int) -> "IntegerScalar":
                result = IntegerScalar()
                result.value = value
                return result

        scalar = IntegerScalar()
        assert isinstance(scalar, ProtocolScalarValue)
        primitive = await scalar.to_primitive()  # Returns 42
        ```
    """

    value: object

    async def to_primitive(self) -> str | int | float | bool | None: ...

    async def from_primitive(
        self, value: str | int | float | bool | None
    ) -> "ProtocolScalarValue": ...


# Checkpoint data structure
@runtime_checkable
class ProtocolCheckpointData(Protocol):
    """
    Protocol for checkpoint data structures in workflow persistence.

    Represents a point-in-time snapshot of workflow state that can be used
    for recovery, replay, or state inspection. Checkpoints enable fault-tolerant
    workflow execution by preserving state at critical points.

    Attributes:
        checkpoint_id: Unique identifier for this checkpoint.
        workflow_id: Identifier of the parent workflow definition.
        workflow_instance_id: UUID of the specific workflow instance.
        sequence_number: Monotonically increasing sequence for ordering.
        timestamp: When the checkpoint was created.
        data: The actual checkpoint state data.
        metadata: Additional context about the checkpoint.
        status: Current checkpoint lifecycle status.
        size_bytes: Size of the checkpoint data in bytes.
        checksum: Optional integrity checksum for validation.
        tags: Categorization tags for filtering and search.

    Example:
        ```python
        class WorkflowCheckpoint:
            '''Checkpoint implementation for workflow state.'''

            checkpoint_id = "chk_001"
            workflow_id = "order_processing"
            workflow_instance_id = UUID("550e8400-e29b-41d4-a716-446655440000")
            sequence_number = 5
            timestamp = datetime.now()
            data = {"order_id": "ORD-123", "status": "processing"}
            metadata = {"created_by": "system"}
            status = "active"
            size_bytes = 1024
            checksum = "sha256:abc123"
            tags = ["orders", "processing"]

            async def validate_checksum(self) -> bool:
                return True  # Verify data integrity

            async def get_data_summary(self) -> dict:
                return {"keys": list(self.data.keys())}

        checkpoint = WorkflowCheckpoint()
        assert isinstance(checkpoint, ProtocolCheckpointData)
        ```
    """

    checkpoint_id: str
    workflow_id: str
    workflow_instance_id: UUID
    sequence_number: int
    timestamp: ProtocolDateTime
    data: dict[str, ContextValue]
    metadata: dict[str, ContextValue]
    status: LiteralCheckpointStatus
    size_bytes: int
    checksum: str | None
    tags: list[str]

    async def validate_checksum(self) -> bool: ...

    async def get_data_summary(self) -> dict[str, ContextValue]: ...


# Storage credentials
@runtime_checkable
class ProtocolStorageCredentials(Protocol):
    """
    Protocol for storage authentication credentials.

    Encapsulates authentication information for connecting to storage backends.
    Supports multiple credential types including username/password, API keys,
    and connection strings. Provides secure handling with data masking.

    Attributes:
        credential_type: Type of credential (e.g., "basic", "api_key", "oauth").
        username: Optional username for basic authentication.
        password: Optional password for basic authentication.
        api_key: Optional API key for key-based authentication.
        connection_string: Optional full connection string.
        endpoint_url: Optional storage service endpoint URL.
        region: Optional cloud region identifier.
        additional_config: Extra configuration parameters.

    Example:
        ```python
        class S3Credentials:
            '''AWS S3 storage credentials.'''

            credential_type = "api_key"
            username = None
            password = None
            api_key = "AKIAIOSFODNN7EXAMPLE"
            connection_string = None
            endpoint_url = "https://s3.amazonaws.com"
            region = "us-east-1"
            additional_config = {"bucket": "my-bucket"}

            async def validate_credentials(self) -> bool:
                return self.api_key is not None

            async def mask_sensitive_data(self) -> dict:
                return {"api_key": "****MPLE", "region": self.region}

        creds = S3Credentials()
        assert isinstance(creds, ProtocolStorageCredentials)
        ```
    """

    credential_type: str
    username: str | None
    password: str | None
    api_key: str | None
    connection_string: str | None
    endpoint_url: str | None
    region: str | None
    additional_config: dict[str, ContextValue]

    async def validate_credentials(self) -> bool: ...

    async def mask_sensitive_data(self) -> dict[str, ContextValue]: ...


# Storage configuration
@runtime_checkable
class ProtocolStorageConfiguration(Protocol):
    """
    Protocol for storage backend configuration.

    Defines comprehensive configuration for storage backends including
    connection parameters, data retention policies, and operational settings.
    Supports multiple backend types with consistent configuration interface.

    Attributes:
        backend_type: Storage backend type (filesystem, postgresql, s3, etc.).
        connection_params: Backend-specific connection parameters.
        retention_hours: Data retention period in hours.
        max_size_bytes: Optional maximum storage capacity.
        compression_enabled: Whether data compression is enabled.
        encryption_enabled: Whether encryption at rest is enabled.
        backup_enabled: Whether automatic backups are enabled.
        health_check_interval: Health check frequency in seconds.
        timeout_seconds: Operation timeout in seconds.
        retry_count: Number of retry attempts for failed operations.
        additional_config: Backend-specific additional settings.

    Example:
        ```python
        class PostgreSQLConfig:
            '''PostgreSQL storage backend configuration.'''

            backend_type = "postgresql"
            connection_params = {
                "host": "localhost",
                "port": 5432,
                "database": "onex_storage"
            }
            retention_hours = 720  # 30 days
            max_size_bytes = 10 * 1024 * 1024 * 1024  # 10GB
            compression_enabled = True
            encryption_enabled = True
            backup_enabled = True
            health_check_interval = 30
            timeout_seconds = 30
            retry_count = 3
            additional_config = {"pool_size": 10}

            async def validate_configuration(self) -> bool:
                return self.backend_type in ["postgresql", "mysql"]

            async def get_connection_string(self) -> str:
                p = self.connection_params
                return f"postgresql://{p['host']}:{p['port']}/{p['database']}"

        config = PostgreSQLConfig()
        assert isinstance(config, ProtocolStorageConfiguration)
        ```
    """

    backend_type: LiteralStorageBackendType
    connection_params: dict[str, ContextValue]
    retention_hours: int
    max_size_bytes: int | None
    compression_enabled: bool
    encryption_enabled: bool
    backup_enabled: bool
    health_check_interval: int
    timeout_seconds: int
    retry_count: int
    additional_config: dict[str, ContextValue]

    async def validate_configuration(self) -> bool: ...

    async def get_connection_string(self) -> str: ...


# Storage operation result
@runtime_checkable
class ProtocolStorageResult(Protocol):
    """
    Protocol for storage operation results.

    Provides standardized result structure for storage operations including
    success/failure indication, timing information, and error details.
    Used for consistent result handling across all storage backends.

    Attributes:
        success: Whether the operation completed successfully.
        operation: Name of the operation performed (e.g., "read", "write").
        message: Human-readable result message.
        data: Optional result data from the operation.
        error_code: Optional error code on failure.
        error_details: Optional detailed error description.
        execution_time_ms: Operation duration in milliseconds.
        timestamp: When the operation completed.
        metadata: Additional operation context.

    Example:
        ```python
        class WriteResult:
            '''Result from a storage write operation.'''

            success = True
            operation = "write"
            message = "Data written successfully"
            data = {"bytes_written": 1024}
            error_code = None
            error_details = None
            execution_time_ms = 45
            timestamp = datetime.now()
            metadata = {"key": "user/123/profile"}

            async def is_successful(self) -> bool:
                return self.success

            async def get_error_info(self) -> dict | None:
                if not self.success:
                    return {"code": self.error_code, "details": self.error_details}
                return None

        result = WriteResult()
        assert isinstance(result, ProtocolStorageResult)
        ```
    """

    success: bool
    operation: str
    message: str
    data: ContextValue | None
    error_code: str | None
    error_details: str | None
    execution_time_ms: int
    timestamp: ProtocolDateTime
    metadata: dict[str, ContextValue]

    async def is_successful(self) -> bool: ...

    async def get_error_info(self) -> dict[str, ContextValue] | None: ...


# Storage list result
@runtime_checkable
class ProtocolStorageListResult(Protocol):
    """
    Protocol for storage list operation results with pagination.

    Provides paginated results for storage listing operations, including
    item data, pagination metadata, and performance metrics. Enables
    efficient retrieval of large datasets in manageable chunks.

    Attributes:
        success: Whether the list operation succeeded.
        items: List of retrieved items as dictionaries.
        total_count: Total number of items matching the query.
        offset: Starting position in the result set.
        limit: Maximum items per page (None for unlimited).
        has_more: Whether additional pages are available.
        execution_time_ms: Query duration in milliseconds.
        timestamp: When the query was executed.
        metadata: Additional query context.

    Example:
        ```python
        class CheckpointListResult:
            '''Paginated list of workflow checkpoints.'''

            success = True
            items = [
                {"id": "chk_001", "workflow": "order_processing"},
                {"id": "chk_002", "workflow": "order_processing"}
            ]
            total_count = 150
            offset = 0
            limit = 50
            has_more = True
            execution_time_ms = 23
            timestamp = datetime.now()
            metadata = {"query": "workflow=order_processing"}

            async def get_paginated_info(self) -> dict:
                return {
                    "page": self.offset // (self.limit or 1),
                    "total_pages": (self.total_count + (self.limit or 1) - 1)
                        // (self.limit or 1),
                    "has_more": self.has_more
                }

        result = CheckpointListResult()
        assert isinstance(result, ProtocolStorageListResult)
        ```
    """

    success: bool
    items: list[dict[str, ContextValue]]
    total_count: int
    offset: int
    limit: int | None
    has_more: bool
    execution_time_ms: int
    timestamp: ProtocolDateTime
    metadata: dict[str, ContextValue]

    async def get_paginated_info(self) -> dict[str, ContextValue]: ...


# Storage health status
@runtime_checkable
class ProtocolStorageHealthStatus(Protocol):
    """
    Protocol for storage health status information.

    Provides comprehensive health monitoring data for storage backends
    including capacity metrics, response times, and individual health checks.
    Used for proactive monitoring and capacity planning.

    Attributes:
        healthy: Overall health status (True if operational).
        status: Detailed health status (healthy, degraded, unhealthy, unknown).
        backend_type: Type of storage backend being monitored.
        total_capacity_bytes: Total storage capacity (if applicable).
        used_capacity_bytes: Currently used capacity (if applicable).
        available_capacity_bytes: Available capacity (if applicable).
        last_check_time: When the health check was performed.
        response_time_ms: Backend response latency in milliseconds.
        error_message: Error details if unhealthy.
        checks: Individual health check results by name.
        metrics: Additional performance metrics.

    Example:
        ```python
        class S3HealthStatus:
            '''Health status for S3 storage backend.'''

            healthy = True
            status = "healthy"
            backend_type = "s3"
            total_capacity_bytes = None  # S3 has unlimited capacity
            used_capacity_bytes = 5 * 1024 * 1024 * 1024  # 5GB used
            available_capacity_bytes = None
            last_check_time = datetime.now()
            response_time_ms = 45
            error_message = None
            checks = {"connectivity": True, "permissions": True}
            metrics = {"objects_count": 1500, "avg_object_size": 3500}

            async def get_capacity_info(self) -> dict:
                return {"used_gb": self.used_capacity_bytes / (1024**3)}

            async def is_healthy(self) -> bool:
                return self.healthy and all(self.checks.values())

        status = S3HealthStatus()
        assert isinstance(status, ProtocolStorageHealthStatus)
        ```
    """

    healthy: bool
    status: LiteralHealthStatus
    backend_type: LiteralStorageBackendType
    total_capacity_bytes: int | None
    used_capacity_bytes: int | None
    available_capacity_bytes: int | None
    last_check_time: ProtocolDateTime
    response_time_ms: int
    error_message: str | None
    checks: dict[str, bool]
    metrics: dict[str, ContextValue]

    async def get_capacity_info(self) -> dict[str, ContextValue]: ...

    async def is_healthy(self) -> bool: ...


# Service health model for database
@runtime_checkable
class ProtocolServiceHealth(Protocol):
    """
    Protocol for service health information.

    Provides comprehensive health status for ONEX services including
    version information, uptime metrics, dependency status, and
    detailed health checks. Essential for distributed system monitoring.

    Attributes:
        service_name: Unique service identifier.
        status: Current health status (healthy, degraded, unhealthy, unknown).
        version: Service version using semantic versioning.
        uptime_seconds: Time since service started.
        last_check_time: When the health check was performed.
        response_time_ms: Service response latency.
        error_message: Error details if unhealthy.
        checks: Individual health check results.
        metrics: Performance and operational metrics.
        dependencies: List of dependent service names.

    Example:
        ```python
        class DatabaseServiceHealth:
            '''Health status for database service.'''

            service_name = "postgresql-primary"
            status = "healthy"
            version = SemVer(major=14, minor=2, patch=0)
            uptime_seconds = 86400  # 1 day
            last_check_time = datetime.now()
            response_time_ms = 12
            error_message = None
            checks = {"connections": True, "replication": True, "disk": True}
            metrics = {"active_connections": 45, "queries_per_second": 150}
            dependencies = ["network", "storage"]

            async def is_healthy(self) -> bool:
                return self.status == "healthy"

            async def get_detailed_status(self) -> dict:
                return {
                    "uptime_hours": self.uptime_seconds / 3600,
                    "checks": self.checks,
                    "metrics": self.metrics
                }

        health = DatabaseServiceHealth()
        assert isinstance(health, ProtocolServiceHealth)
        ```
    """

    service_name: str
    status: LiteralHealthStatus
    version: ProtocolSemVer
    uptime_seconds: int
    last_check_time: ProtocolDateTime
    response_time_ms: int
    error_message: str | None
    checks: dict[str, bool]
    metrics: dict[str, ContextValue]
    dependencies: list[str]

    async def is_healthy(self) -> bool: ...

    async def get_detailed_status(self) -> dict[str, ContextValue]: ...


# Database row type
@runtime_checkable
class ProtocolDatabaseRow(Protocol):
    """
    Protocol for database row representation.

    Provides a structured representation of a single database row with
    type information for each column. Supports type-safe value access
    and column introspection for dynamic data handling.

    Attributes:
        data: Column name to value mapping.
        column_types: Column name to SQL type mapping.
        table_name: Source table name (if available).

    Example:
        ```python
        class UserRow:
            '''Row from the users table.'''

            data = {"id": 1, "name": "Alice", "active": True}
            column_types = {"id": "INTEGER", "name": "VARCHAR", "active": "BOOLEAN"}
            table_name = "users"

            async def get_value(self, column_name: str):
                return self.data.get(column_name)

            async def has_column(self, column_name: str) -> bool:
                return column_name in self.data

        row = UserRow()
        assert isinstance(row, ProtocolDatabaseRow)
        name = await row.get_value("name")  # Returns "Alice"
        ```
    """

    data: dict[str, str | int | float | bool | None]
    column_types: dict[str, str]
    table_name: str | None

    async def get_value(self, column_name: str) -> str | int | float | bool | None: ...

    async def has_column(self, column_name: str) -> bool: ...


# Query result
@runtime_checkable
class ProtocolQueryResult(Protocol):
    """
    Protocol for database query results.

    Encapsulates the results of a database query including returned rows,
    execution metrics, and convenience methods for data access. Supports
    both SELECT queries (with rows) and DML operations (with affected_rows).

    Attributes:
        success: Whether the query executed successfully.
        rows: List of returned rows for SELECT queries.
        row_count: Number of rows in the result set.
        execution_time_ms: Query execution duration.
        affected_rows: Rows affected by DML operations (INSERT/UPDATE/DELETE).
        query_type: Type of database operation performed.
        timestamp: When the query was executed.
        metadata: Additional query context and statistics.

    Example:
        ```python
        class SelectResult:
            '''Result from a SELECT query.'''

            success = True
            rows = [UserRow(), UserRow()]  # ProtocolDatabaseRow instances
            row_count = 2
            execution_time_ms = 15
            affected_rows = None
            query_type = "select"
            timestamp = datetime.now()
            metadata = {"query": "SELECT * FROM users WHERE active = true"}

            async def get_first_row(self) -> ProtocolDatabaseRow | None:
                return self.rows[0] if self.rows else None

            async def get_value_at(self, row_index: int, column_name: str):
                if row_index < len(self.rows):
                    return await self.rows[row_index].get_value(column_name)
                return None

        result = SelectResult()
        assert isinstance(result, ProtocolQueryResult)
        first_user = await result.get_first_row()
        ```
    """

    success: bool
    rows: list[ProtocolDatabaseRow]
    row_count: int
    execution_time_ms: int
    affected_rows: int | None
    query_type: LiteralDatabaseOperationType
    timestamp: ProtocolDateTime
    metadata: dict[str, ContextValue]

    async def get_first_row(self) -> ProtocolDatabaseRow | None: ...

    async def get_value_at(
        self, row_index: int, column_name: str
    ) -> str | int | float | bool | None: ...


# Transaction result
@runtime_checkable
class ProtocolTransactionResult(Protocol):
    """
    Protocol for database transaction results.

    Represents the outcome of a database transaction including commit/rollback
    status, execution metrics, and error information. Provides atomicity
    guarantees for multi-statement database operations.

    Attributes:
        success: Whether the transaction committed successfully.
        transaction_id: Unique identifier for this transaction.
        commands_executed: Number of SQL statements executed.
        execution_time_ms: Total transaction duration.
        rollback_required: Whether rollback is/was needed.
        error_message: Error details if transaction failed.
        timestamp: When the transaction completed.
        metadata: Additional transaction context.

    Example:
        ```python
        class TransferTransaction:
            '''Result from a funds transfer transaction.'''

            success = True
            transaction_id = "txn_abc123"
            commands_executed = 3  # BEGIN, UPDATE (x2), COMMIT
            execution_time_ms = 45
            rollback_required = False
            error_message = None
            timestamp = datetime.now()
            metadata = {"from_account": "A001", "to_account": "A002"}

            async def is_committed(self) -> bool:
                return self.success and not self.rollback_required

            async def get_rollback_reason(self) -> str | None:
                return self.error_message if self.rollback_required else None

        result = TransferTransaction()
        assert isinstance(result, ProtocolTransactionResult)
        if await result.is_committed():
            print("Transfer completed successfully")
        ```
    """

    success: bool
    transaction_id: str
    commands_executed: int
    execution_time_ms: int
    rollback_required: bool
    error_message: str | None
    timestamp: ProtocolDateTime
    metadata: dict[str, ContextValue]

    async def is_committed(self) -> bool: ...

    async def get_rollback_reason(self) -> str | None: ...


# Lock result
@runtime_checkable
class ProtocolLockResult(Protocol):
    """
    Protocol for database lock operation results.

    Represents the outcome of acquiring or releasing a distributed lock,
    including lock metadata, expiration information, and validity checks.
    Essential for coordinating concurrent access in distributed systems.

    Attributes:
        success: Whether the lock operation succeeded.
        lock_name: Unique name identifying the lock.
        lock_token: Token for lock ownership verification.
        acquired_at: When the lock was acquired.
        expires_at: When the lock will automatically release.
        timeout_seconds: Lock acquisition timeout.
        holder_info: Information about the lock holder.

    Example:
        ```python
        class ResourceLock:
            '''Distributed lock for resource coordination.'''

            success = True
            lock_name = "workflow/order_processing/instance_001"
            lock_token = "lck_xyz789"
            acquired_at = datetime.now()
            expires_at = datetime.now() + timedelta(seconds=300)
            timeout_seconds = 300
            holder_info = {"node_id": "worker-01", "pid": 12345}

            async def is_valid(self) -> bool:
                return self.success and datetime.now() < self.expires_at

            async def get_remaining_time(self) -> int:
                if self.expires_at:
                    delta = self.expires_at - datetime.now()
                    return max(0, int(delta.total_seconds()))
                return 0

        lock = ResourceLock()
        assert isinstance(lock, ProtocolLockResult)
        if await lock.is_valid():
            print(f"Lock valid for {await lock.get_remaining_time()}s")
        ```
    """

    success: bool
    lock_name: str
    lock_token: str | None
    acquired_at: ProtocolDateTime | None
    expires_at: ProtocolDateTime | None
    timeout_seconds: int
    holder_info: dict[str, ContextValue] | None

    async def is_valid(self) -> bool: ...

    async def get_remaining_time(self) -> int: ...


# Connection information
@runtime_checkable
class ProtocolConnectionInfo(Protocol):
    """
    Protocol for database connection information.

    Provides comprehensive information about a database connection including
    connection pooling statistics, activity tracking, and health metrics.
    Used for connection monitoring and capacity management.

    Attributes:
        connection_id: Unique identifier for this connection.
        database_type: Type of database (postgresql, mysql, etc.).
        host: Database server hostname or IP.
        port: Database server port.
        database_name: Name of the connected database.
        username: Authenticated username.
        connected_at: When the connection was established.
        last_activity: Most recent activity timestamp.
        is_active: Whether the connection is currently in use.
        pool_size: Configured connection pool size.
        active_connections: Currently active connections in pool.
        idle_connections: Idle connections available in pool.
        max_connections: Maximum allowed connections.
        timeout_seconds: Connection timeout setting.
        metadata: Additional connection properties.

    Example:
        ```python
        class PostgresConnectionInfo:
            '''PostgreSQL connection pool information.'''

            connection_id = "conn_pg_001"
            database_type = "postgresql"
            host = "db.example.com"
            port = 5432
            database_name = "onex_production"
            username = "app_user"
            connected_at = datetime.now() - timedelta(hours=2)
            last_activity = datetime.now()
            is_active = True
            pool_size = 20
            active_connections = 8
            idle_connections = 12
            max_connections = 100
            timeout_seconds = 30
            metadata = {"ssl": True, "schema": "public"}

            async def get_utilization_stats(self) -> dict:
                return {
                    "utilization_percent": (self.active_connections / self.pool_size) * 100,
                    "available": self.idle_connections
                }

            async def is_healthy(self) -> bool:
                return self.is_active and self.active_connections < self.max_connections

        conn_info = PostgresConnectionInfo()
        assert isinstance(conn_info, ProtocolConnectionInfo)
        ```
    """

    connection_id: str
    database_type: str
    host: str
    port: int
    database_name: str
    username: str
    connected_at: ProtocolDateTime
    last_activity: ProtocolDateTime
    is_active: bool
    pool_size: int
    active_connections: int
    idle_connections: int
    max_connections: int
    timeout_seconds: int
    metadata: dict[str, ContextValue]

    async def get_utilization_stats(self) -> dict[str, ContextValue]: ...

    async def is_healthy(self) -> bool: ...
