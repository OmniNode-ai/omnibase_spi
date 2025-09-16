"""
ONEX Event Bus Protocols - SPI Interface Exports.

Event-driven messaging protocols supporting the ONEX Messaging Design v0.3:
- EventBusAdapter for pluggable Kafka/Redpanda backends
- Environment isolation and node group mini-meshes  
- Distributed messaging with standardized interfaces
- Event bus service protocols
"""

from .protocol_event_bus import (
    ProtocolEventBus,
    ProtocolEventBusAdapter,
    ProtocolEventMessage,
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
    EventBusAdapterType,
    EventBusServiceType,
    ProtocolEventBusService,
)
from .protocol_kafka_adapter import ProtocolKafkaAdapter
from .protocol_redpanda_adapter import ProtocolRedpandaAdapter

__all__ = [
    # Core event bus abstractions
    "ProtocolEventMessage",
    "ProtocolEventBusAdapter",
    "ProtocolEventBus",
    # Context management and in-memory protocols
    "ProtocolEventBusContextManager",
    "ProtocolEventBusInMemory",
    # Mixin protocols
    "ProtocolEventBusBase",
    "ProtocolSyncEventBus",
    "ProtocolAsyncEventBus",
    "ProtocolRegistryWithBus",
    "ProtocolLogEmitter",
    # Backend adapter protocols
    "ProtocolKafkaAdapter",
    "ProtocolRedpandaAdapter",
    # Service protocols
    "ProtocolEventBusService",
    "EventBusServiceType",
    "EventBusAdapterType",
]
