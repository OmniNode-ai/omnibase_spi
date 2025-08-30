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

    @property
    def redpanda_optimized_defaults(self) -> dict[str, str]:
        """Get Redpanda-optimized configuration defaults."""
        ...
