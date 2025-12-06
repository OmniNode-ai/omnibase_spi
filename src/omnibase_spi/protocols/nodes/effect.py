"""Effect node protocol for side-effecting operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.nodes.base import ProtocolNode

if TYPE_CHECKING:
    from omnibase_core.models.effect import ModelEffectInput, ModelEffectOutput


@runtime_checkable
class ProtocolEffectNode(ProtocolNode, Protocol):
    """
    Protocol for effect nodes.

    Effect nodes perform side-effecting operations such as:
        - External API calls (HTTP, gRPC)
        - Database operations (read/write)
        - Message queue interactions (Kafka, RabbitMQ)
        - File system operations

    Unlike compute nodes, effect nodes:
        - Have side effects (I/O operations)
        - May not be deterministic
        - Require lifecycle management (initialize/shutdown)
        - Often delegate to ProtocolHandlers for actual I/O

    Example implementations:
        - HTTP API client nodes
        - Database query nodes
        - Message publishing nodes
        - File processing nodes
    """

    async def initialize(self) -> None:
        """
        Initialize node-specific resources if needed.

        Called before the first execute() to set up connections,
        load contracts, initialize handlers, etc.

        Raises:
            HandlerInitializationError: If initialization fails.
        """
        ...

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """
        Release node-specific resources if needed.

        Called during graceful shutdown to close connections,
        flush pending operations, and release resources.

        Args:
            timeout_seconds: Maximum time to wait for shutdown to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If shutdown does not complete within the specified timeout.
        """
        ...

    async def execute(
        self,
        input_data: ModelEffectInput,
    ) -> ModelEffectOutput:
        """
        Execute effect operation.

        Args:
            input_data: Effect input model from core.

        Returns:
            Effect output model from core.

        Raises:
            ProtocolHandlerError: If effect execution fails.
            SPIError: For other SPI-related errors.
        """
        ...
