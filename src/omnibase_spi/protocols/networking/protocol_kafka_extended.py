"""
DEPRECATED: This module is deprecated and will be removed in v0.5.0.

Use omnibase_spi.protocols.event_bus.protocol_event_bus_extended instead.

Migration guide:
    Old: from omnibase_spi.protocols.networking import ProtocolKafkaMessage
    New: from omnibase_spi.protocols.event_bus import ProtocolEventBusMessage

    Old: from omnibase_spi.protocols.networking import ProtocolKafkaConsumer
    New: from omnibase_spi.protocols.event_bus import ProtocolEventBusConsumer

    Old: from omnibase_spi.protocols.networking import ProtocolKafkaBatchProducer
    New: from omnibase_spi.protocols.event_bus import ProtocolEventBusBatchProducer

    Old: from omnibase_spi.protocols.networking import ProtocolKafkaTransactionalProducer
    New: from omnibase_spi.protocols.event_bus import ProtocolEventBusTransactionalProducer

    Old: from omnibase_spi.protocols.networking import ProtocolKafkaExtendedClient
    New: from omnibase_spi.protocols.event_bus import ProtocolEventBusExtendedClient
"""

import warnings

from omnibase_spi.protocols.event_bus.protocol_event_bus_extended import (
    ProtocolEventBusBatchProducer,
    ProtocolEventBusConsumer,
    ProtocolEventBusExtendedClient,
    ProtocolEventBusMessage,
    ProtocolEventBusTransactionalProducer,
)


def __getattr__(name: str) -> type:
    """Provide deprecated aliases for backwards compatibility."""
    if name == "ProtocolKafkaMessage":
        warnings.warn(
            "ProtocolKafkaMessage is deprecated, use ProtocolEventBusMessage instead. "
            "Will be removed in v0.5.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return ProtocolEventBusMessage
    if name == "ProtocolKafkaConsumer":
        warnings.warn(
            "ProtocolKafkaConsumer is deprecated, use ProtocolEventBusConsumer instead. "
            "Will be removed in v0.5.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return ProtocolEventBusConsumer
    if name == "ProtocolKafkaBatchProducer":
        warnings.warn(
            "ProtocolKafkaBatchProducer is deprecated, use ProtocolEventBusBatchProducer instead. "
            "Will be removed in v0.5.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return ProtocolEventBusBatchProducer
    if name == "ProtocolKafkaTransactionalProducer":
        warnings.warn(
            "ProtocolKafkaTransactionalProducer is deprecated, use ProtocolEventBusTransactionalProducer instead. "
            "Will be removed in v0.5.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return ProtocolEventBusTransactionalProducer
    if name == "ProtocolKafkaExtendedClient":
        warnings.warn(
            "ProtocolKafkaExtendedClient is deprecated, use ProtocolEventBusExtendedClient instead. "
            "Will be removed in v0.5.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return ProtocolEventBusExtendedClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Deprecated aliases (remove in v0.5.0)
    "ProtocolKafkaMessage",
    "ProtocolKafkaConsumer",
    "ProtocolKafkaBatchProducer",
    "ProtocolKafkaTransactionalProducer",
    "ProtocolKafkaExtendedClient",
    # New names (preferred)
    "ProtocolEventBusMessage",
    "ProtocolEventBusConsumer",
    "ProtocolEventBusBatchProducer",
    "ProtocolEventBusTransactionalProducer",
    "ProtocolEventBusExtendedClient",
]
