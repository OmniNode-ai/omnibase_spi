"""
Storage types for ONEX SPI interfaces.

Domain: Storage and checkpoint management types
"""

from typing import Any, Literal, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralHealthStatus,
    LiteralOperationStatus,
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
    """Protocol for scalar values in database operations."""

    value: Any

    async def to_primitive(self) -> str | int | float | bool | None: ...

    async def from_primitive(
        self, value: str | int | float | bool | None
    ) -> "ProtocolScalarValue": ...


# Checkpoint data structure
@runtime_checkable
class ProtocolCheckpointData(Protocol):
    """Protocol for checkpoint data structures."""

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
    """Protocol for storage authentication credentials."""

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
    """Protocol for storage backend configuration."""

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
    """Protocol for storage operation results."""

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
    """Protocol for storage list operation results."""

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
    """Protocol for storage health status information."""

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
    """Protocol for service health information."""

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
    """Protocol for database row representation."""

    data: dict[str, str | int | float | bool | None]
    column_types: dict[str, str]
    table_name: str | None

    async def get_value(self, column_name: str) -> str | int | float | bool | None: ...

    async def has_column(self, column_name: str) -> bool: ...


# Query result
@runtime_checkable
class ProtocolQueryResult(Protocol):
    """Protocol for database query results."""

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
    """Protocol for database transaction results."""

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
    """Protocol for database lock operations."""

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
    """Protocol for database connection information."""

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
