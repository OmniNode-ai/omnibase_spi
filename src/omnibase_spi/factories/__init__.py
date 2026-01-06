"""Factory protocol interfaces for omnibase_spi.

This module provides factory protocol interfaces for creating
handler contracts and other SPI objects. The protocols define
the interface; concrete implementations belong in omnibase_infra.

Note:
    The concrete `HandlerContractFactory` implementation has been moved
    to omnibase_infra. This module now exports only the Protocol interface.
"""

from omnibase_spi.protocols.factories import ProtocolHandlerContractFactory

__all__ = [
    "ProtocolHandlerContractFactory",
]
