"""
DEPRECATED: This module is deprecated and will be removed in v0.5.0.

Use omnibase_spi.protocols.event_bus.protocol_event_bus_client instead.

Migration guide:
    Old: from omnibase_spi.protocols.networking import ProtocolKafkaClient
    New: from omnibase_spi.protocols.event_bus import ProtocolEventBusClient

    Old: from omnibase_spi.protocols.networking import ProtocolKafkaClientProvider
    New: from omnibase_spi.protocols.event_bus import ProtocolEventBusClientProvider
"""

import warnings

from omnibase_spi.protocols.event_bus.protocol_event_bus_client import (
    ProtocolEventBusClient,
    ProtocolEventBusClientProvider,
)


def __getattr__(name: str) -> type:
    """Provide deprecated aliases for backwards compatibility."""
    if name == "ProtocolKafkaClient":
        warnings.warn(
            "ProtocolKafkaClient is deprecated, use ProtocolEventBusClient instead. "
            "Will be removed in v0.5.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return ProtocolEventBusClient
    if name == "ProtocolKafkaClientProvider":
        warnings.warn(
            "ProtocolKafkaClientProvider is deprecated, use ProtocolEventBusClientProvider instead. "
            "Will be removed in v0.5.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return ProtocolEventBusClientProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Deprecated aliases (remove in v0.5.0)
    "ProtocolKafkaClient",
    "ProtocolKafkaClientProvider",
    # New names (preferred)
    "ProtocolEventBusClient",
    "ProtocolEventBusClientProvider",
]
