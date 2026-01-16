"""Protocol for Kafka event bus bootstrap operations."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_mcp_types import (
    ProtocolEventBusBootstrapResult,
    ProtocolEventBusConfig,
)


@runtime_checkable
class ProtocolToolBootstrap(Protocol):
    """
    Protocol for bootstrap tool for the Kafka event bus node.
    Accepts a strongly-typed ModelEventBusConfig and returns a ModelEventBusBootstrapResult.
    """

    async def bootstrap_kafka_cluster(
        self,
        config: ProtocolEventBusConfig,
    ) -> ProtocolEventBusBootstrapResult:
        """
        Perform bootstrap initialization for the Kafka cluster.
        Args:
            config: ModelEventBusConfig
        Returns:
            ModelEventBusBootstrapResult
        """
        ...
