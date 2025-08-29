#!/usr/bin/env python3
"""
Redpanda Event Bus Adapter Protocol - ONEX SPI Interface.

Protocol definition for Redpanda backend implementations.
Redpanda is Kafka API compatible with optimized defaults.
"""

from typing import Protocol, runtime_checkable

from .protocol_kafka_adapter import ProtocolKafkaAdapter


@runtime_checkable
class ProtocolRedpandaAdapter(ProtocolKafkaAdapter, Protocol):
    """
    Protocol for Redpanda event bus adapter implementations.

    Extends ProtocolKafkaAdapter since Redpanda uses Kafka protocol
    but with Redpanda-optimized defaults and configurations.
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        environment: str = "dev",
        group: str = "default",
        **redpanda_config,
    ):
        """
        Initialize Redpanda adapter with optimized defaults.

        Args:
            bootstrap_servers: Redpanda broker addresses
            environment: Environment name for topic isolation
            group: Tool group name for mini-mesh isolation
            **redpanda_config: Redpanda-specific configuration overrides
        """
        ...

    @property
    def redpanda_optimized_defaults(self) -> dict:
        """Get Redpanda-optimized configuration defaults."""
        ...
