"""
ONEX Event Bus Protocols - SPI Interface Exports.

Event-driven messaging protocols supporting the ONEX Messaging Design v0.3:
- EventBusProvider for factory-based event bus instance management
- Environment isolation and node group mini-meshes
- Distributed messaging with standardized interfaces
- Event bus service protocols

Note:
    Core interface protocols (ProtocolEventBus, ProtocolEventBusHeaders,
    ProtocolKafkaEventBusAdapter) are imported from omnibase_core.
    This module exports only SPI-specific factory and service protocols.
"""

from ..types.protocol_event_bus_types import ProtocolEventMessage
from .protocol_dlq_handler import ProtocolDLQHandler
from .protocol_event_bus_context_manager import ProtocolEventBusContextManager
from .protocol_event_bus_mixin import (
    ProtocolAsyncEventBus,
    ProtocolEventBusBase,
    ProtocolEventBusLogEmitter,
    ProtocolEventBusRegistry,
    ProtocolSyncEventBus,
)
from .protocol_event_bus_producer_handler import ProtocolEventBusProducerHandler
from .protocol_event_bus_provider import ProtocolEventBusProvider
from .protocol_event_bus_service import (
    ProtocolEventBusService,
    ProtocolHttpEventBusAdapter,
)

# Phase 1: Event Bus Foundation
from .protocol_event_envelope import ProtocolEventEnvelope
from .protocol_event_publisher import ProtocolEventPublisher
from .protocol_kafka_adapter import ProtocolKafkaAdapter
from .protocol_redpanda_adapter import ProtocolRedpandaAdapter
from .protocol_schema_registry import ProtocolSchemaRegistry

__all__ = [
    "ProtocolAsyncEventBus",
    "ProtocolDLQHandler",
    "ProtocolEventBusBase",
    "ProtocolEventBusContextManager",
    "ProtocolEventBusLogEmitter",
    "ProtocolEventBusProducerHandler",
    "ProtocolEventBusProvider",
    "ProtocolEventBusRegistry",
    "ProtocolEventBusService",
    # Phase 1: Event Bus Foundation
    "ProtocolEventEnvelope",
    "ProtocolEventMessage",
    "ProtocolEventPublisher",
    "ProtocolHttpEventBusAdapter",
    "ProtocolKafkaAdapter",
    "ProtocolRedpandaAdapter",
    "ProtocolSchemaRegistry",
    "ProtocolSyncEventBus",
]
