"""Registry interfaces for omnibase_spi v0.4.0."""

from omnibase_spi.protocols.registry.handler_registry import ProtocolHandlerRegistry
from omnibase_spi.protocols.registry.protocol_registry_base import ProtocolRegistryBase
from omnibase_spi.protocols.registry.protocol_versioned_registry import (
    ProtocolVersionedRegistry,
)

__all__ = [
    "ProtocolHandlerRegistry",
    "ProtocolRegistryBase",
    "ProtocolVersionedRegistry",
]
