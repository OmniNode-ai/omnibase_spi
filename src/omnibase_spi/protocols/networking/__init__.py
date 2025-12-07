"""Protocols for network communication, HTTP requests, and data exchange.

Note:
    Kafka-specific protocols are deprecated and will be removed in v0.5.0.
    Use the backend-agnostic EventBus protocols from omnibase_spi.protocols.event_bus instead.
"""

from __future__ import annotations

from .protocol_circuit_breaker import ProtocolCircuitBreaker
from .protocol_communication_bridge import ProtocolCommunicationBridge
from .protocol_http_client import ProtocolHttpClient
from .protocol_http_extended import ProtocolHttpExtendedClient

# Import deprecated Kafka protocols with re-exports to new EventBus protocols
# These modules now emit DeprecationWarning when old names are accessed
from .protocol_kafka_client import (
    ProtocolEventBusClient,
    ProtocolEventBusClientProvider,
)
from .protocol_kafka_extended import (
    ProtocolEventBusBatchProducer,
    ProtocolEventBusConsumer,
    ProtocolEventBusExtendedClient,
    ProtocolEventBusMessage,
    ProtocolEventBusTransactionalProducer,
)

__all__ = [
    # Core networking protocols
    "ProtocolCircuitBreaker",
    "ProtocolCommunicationBridge",
    "ProtocolHttpClient",
    "ProtocolHttpExtendedClient",
    # New EventBus protocols (backend-agnostic, preferred)
    "ProtocolEventBusClient",
    "ProtocolEventBusClientProvider",
    "ProtocolEventBusMessage",
    "ProtocolEventBusConsumer",
    "ProtocolEventBusBatchProducer",
    "ProtocolEventBusTransactionalProducer",
    "ProtocolEventBusExtendedClient",
    # DEPRECATED: Kafka-specific names (remove in v0.5.0)
    # Access these via module attribute to get DeprecationWarning
    "ProtocolKafkaClient",
    "ProtocolKafkaClientProvider",
    "ProtocolKafkaMessage",
    "ProtocolKafkaConsumer",
    "ProtocolKafkaBatchProducer",
    "ProtocolKafkaTransactionalProducer",
    "ProtocolKafkaExtendedClient",
]


def __getattr__(name: str) -> object:
    """Provide deprecated Kafka protocol aliases with warnings."""
    from . import protocol_kafka_client, protocol_kafka_extended

    # Delegate to the appropriate module's __getattr__
    kafka_client_names = {"ProtocolKafkaClient", "ProtocolKafkaClientProvider"}
    kafka_extended_names = {
        "ProtocolKafkaMessage",
        "ProtocolKafkaConsumer",
        "ProtocolKafkaBatchProducer",
        "ProtocolKafkaTransactionalProducer",
        "ProtocolKafkaExtendedClient",
    }

    if name in kafka_client_names:
        return getattr(protocol_kafka_client, name)
    if name in kafka_extended_names:
        return getattr(protocol_kafka_extended, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
