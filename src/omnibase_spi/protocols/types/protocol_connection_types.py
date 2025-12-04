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
    """Protocol for connection configuration."""

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
    """Protocol for connection status tracking."""

    state: LiteralConnectionState
    connected_at: "ProtocolDateTime | None"
    last_activity: "ProtocolDateTime | None"
    error_count: int
    bytes_sent: int
    bytes_received: int

    async def validate_connection_status(self) -> bool: ...

    async def is_connected(self) -> bool: ...
