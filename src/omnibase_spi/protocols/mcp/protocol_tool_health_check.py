"""Protocol for Kafka event bus health check operations."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_mcp_types import (
    ProtocolEventBusConfig,
    ProtocolKafkaHealthCheckResult,
)


@runtime_checkable
class ProtocolToolHealthCheck(Protocol):
    """
    Protocol for health check tool for the Kafka event bus node.
    Accepts a strongly-typed ModelEventBusConfig and returns a KafkaHealthCheckResult.
    """

    async def health_check(
        self, config: ProtocolEventBusConfig
    ) -> ProtocolKafkaHealthCheckResult:
        """
        Perform a health check on the Kafka event bus backend.
        Args:
            config: ModelEventBusConfig
        Returns:
            KafkaHealthCheckResult: The result of the health check
        """
        ...
