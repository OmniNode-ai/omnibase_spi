#!/usr/bin/env python3
"""
Kafka Event Bus Adapter Protocol - ONEX SPI Interface.

Protocol definition for Kafka backend implementations.
Defines the contract for Kafka-specific event bus adapters.
"""

from typing import Dict, Optional, Protocol, runtime_checkable

from .protocol_event_bus import ProtocolEventBusAdapter


@runtime_checkable
class ProtocolKafkaAdapter(ProtocolEventBusAdapter, Protocol):
    """
    Protocol for Kafka event bus adapter implementations.

    Extends ProtocolEventBusAdapter with Kafka-specific configuration
    and connection management protocols.
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        environment: str = "dev",
        group: str = "default",
        **kafka_config,
    ):
        """
        Initialize Kafka adapter.

        Args:
            bootstrap_servers: Kafka broker addresses
            environment: Environment name for topic isolation
            group: Tool group name for mini-mesh isolation
            **kafka_config: Additional Kafka configuration
        """
        ...

    @property
    def bootstrap_servers(self) -> str:
        """Get Kafka bootstrap servers configuration."""
        ...

    @property
    def kafka_config(self) -> Dict[str, object]:
        """Get Kafka-specific configuration."""
        ...

    def build_topic_name(self, topic: str) -> str:
        """
        Build topic name with ONEX naming conventions.

        Format: onex.{environment}.{group}.{topic}
        """
        ...
