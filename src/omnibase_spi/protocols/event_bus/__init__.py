"""
ONEX Event Bus Protocols - SPI Interface Exports.

Event-driven messaging protocols supporting the ONEX Messaging Design v0.3:
- EventBusAdapter for pluggable Kafka/Redpanda backends
- Environment isolation and node group mini-meshes
- Distributed messaging with standardized interfaces
- Event bus service protocols
"""

from ..types.protocol_event_bus_types import ProtocolEventMessage
from .protocol_event_bus import (
    ProtocolEventBus,
    ProtocolEventBusHeaders,
    ProtocolKafkaEventBusAdapter,
)
from .protocol_event_bus_context_manager import ProtocolEventBusContextManager
from .protocol_event_bus_in_memory import ProtocolEventBusInMemory
from .protocol_event_bus_mixin import (
    ProtocolAsyncEventBus,
    ProtocolEventBusBase,
    ProtocolLogEmitter,
    ProtocolRegistryWithBus,
    ProtocolSyncEventBus,
)
from .protocol_event_bus_service import (
    ProtocolEventBusService,
    ProtocolHttpEventBusAdapter,
)
from .protocol_kafka_adapter import ProtocolKafkaAdapter
from .protocol_redpanda_adapter import ProtocolRedpandaAdapter

__all__ = [
    "ProtocolAsyncEventBus",
    "ProtocolEventBus",
    "ProtocolEventBusBase",
    "ProtocolEventBusContextManager",
    "ProtocolEventBusHeaders",
    "ProtocolEventBusInMemory",
    "ProtocolEventBusService",
    "ProtocolEventMessage",
    "ProtocolHttpEventBusAdapter",
    "ProtocolKafkaAdapter",
    "ProtocolKafkaEventBusAdapter",
    "ProtocolLogEmitter",
    "ProtocolRedpandaAdapter",
    "ProtocolRegistryWithBus",
    "ProtocolSyncEventBus",
]
