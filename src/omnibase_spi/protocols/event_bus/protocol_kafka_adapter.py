"""
Kafka Event Bus Adapter Protocol - ONEX SPI Interface.

Protocol definition for Kafka backend implementations.
Defines the contract for Kafka-specific event bus adapters.
"""

from typing import Optional, Protocol, runtime_checkable

from .protocol_event_bus import ProtocolKafkaEventBusAdapter


@runtime_checkable
class ProtocolKafkaConfig(Protocol):
    """Protocol for Kafka configuration parameters."""

    security_protocol: str
    sasl_mechanism: str
    sasl_username: str | None
    sasl_password: str | None
    ssl_cafile: str | None
    auto_offset_reset: str
    enable_auto_commit: bool
    session_timeout_ms: int
    request_timeout_ms: int


@runtime_checkable
class ProtocolKafkaAdapter(ProtocolKafkaEventBusAdapter, Protocol):
    """
    Protocol for Kafka event bus adapter implementations.

    Extends ProtocolKafkaEventBusAdapter with Kafka-specific configuration
    and connection management protocols.
    """

    @property
    def bootstrap_servers(self) -> str: ...

    @property
    def environment(self) -> str: ...

    @property
    def group(self) -> str: ...

    @property
    def config(self) -> ProtocolKafkaConfig | None: ...

    @property
    def kafka_config(self) -> ProtocolKafkaConfig: ...

    async def build_topic_name(self, topic: str) -> str: ...
