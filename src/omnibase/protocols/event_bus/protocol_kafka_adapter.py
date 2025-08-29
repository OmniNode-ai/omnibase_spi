#!/usr/bin/env python3
"""
Kafka Event Bus Adapter Protocol - ONEX SPI Interface.

Protocol definition for Kafka backend implementations.
Defines the contract for Kafka-specific event bus adapters.
"""

from typing import Optional, Protocol, runtime_checkable

from .protocol_event_bus import ProtocolEventBusAdapter


@runtime_checkable
class ProtocolKafkaConfig(Protocol):
    """Protocol for Kafka configuration parameters."""

    security_protocol: str
    sasl_mechanism: str
    sasl_username: Optional[str]
    sasl_password: Optional[str]
    ssl_cafile: Optional[str]
    auto_offset_reset: str
    enable_auto_commit: bool
    session_timeout_ms: int
    request_timeout_ms: int


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
        config: Optional[ProtocolKafkaConfig] = None,
    ):
        """
        Initialize Kafka adapter.

        Args:
            bootstrap_servers: Kafka broker addresses
            environment: Environment name for topic isolation
            group: Tool group name for mini-mesh isolation
            config: Optional Kafka configuration protocol
        """
        ...

    @property
    def bootstrap_servers(self) -> str:
        """Get Kafka bootstrap servers configuration."""
        ...

    @property
    def kafka_config(self) -> ProtocolKafkaConfig:
        """Get Kafka-specific configuration."""
        ...

    def build_topic_name(self, topic: str) -> str:
        """
        Build topic name with ONEX naming conventions.

        Format: onex.{environment}.{group}.{topic}
        """
        ...
