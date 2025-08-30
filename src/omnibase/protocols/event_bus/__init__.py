"""
ONEX Event Bus Protocols - SPI Interface Exports.

Event-driven messaging protocols supporting the ONEX Messaging Design v0.3:
- EventBusAdapter for pluggable Kafka/Redpanda backends
- Environment isolation and node group mini-meshes  
- Distributed messaging with standardized interfaces
"""

from .protocol_event_bus import (
    ProtocolEventBus,
    ProtocolEventBusAdapter,
    ProtocolEventMessage,
)
from .protocol_kafka_adapter import ProtocolKafkaAdapter
from .protocol_redpanda_adapter import ProtocolRedpandaAdapter

__all__ = [
    # Core event bus abstractions
    "ProtocolEventMessage",
    "ProtocolEventBusAdapter",
    "ProtocolEventBus",
    # Backend adapter protocols
    "ProtocolKafkaAdapter",
    "ProtocolRedpandaAdapter",
]
