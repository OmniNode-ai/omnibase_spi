"""Protocol handler interface for DI-based effect nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.protocol import (
        ModelConnectionConfig,
        ModelOperationConfig,
        ModelProtocolRequest,
        ModelProtocolResponse,
    )


@runtime_checkable
class ProtocolHandler(Protocol):
    """
    Protocol for protocol-specific handlers (HTTP, Kafka, DB, etc.).

    Implementations live in `omnibase_core` or `omnibase_infra`.
    This interface enables dependency injection of I/O handlers
    into effect nodes without tight coupling.

    Example implementations:
        - HttpRestHandler: HTTP/REST API calls
        - BoltHandler: Neo4j Cypher queries
        - PostgresHandler: SQL queries via asyncpg
        - KafkaHandler: Message publishing
    """

    async def initialize(
        self,
        config: "ModelConnectionConfig",
    ) -> None:
        """
        Initialize any clients or connection pools.

        Args:
            config: Connection configuration including URL, auth, pool settings.

        Raises:
            HandlerInitializationError: If initialization fails.
        """
        ...

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """
        Release resources and close connections.

        Should flush pending operations and release all resources gracefully.

        Args:
            timeout_seconds: Maximum time to wait for shutdown to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If shutdown does not complete within the specified timeout.
        """
        ...

    async def execute(
        self,
        request: "ModelProtocolRequest",
        operation_config: "ModelOperationConfig",
    ) -> "ModelProtocolResponse":
        """
        Execute a protocol-specific operation.

        Args:
            request: Protocol-agnostic request model from core.
            operation_config: Operation-specific config from core.

        Returns:
            Protocol-agnostic response model from core.

        Raises:
            ProtocolHandlerError: If execution fails.
        """
        ...
