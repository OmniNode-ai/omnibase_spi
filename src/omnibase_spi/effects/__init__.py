"""Effect node protocol definitions for omnibase_spi.

This package contains SPI-level effect node protocols used as
synchronous execution boundaries by the ONEX runtime.
"""

from omnibase_spi.effects.node_projection_effect import ProtocolNodeProjectionEffect

__all__ = [
    "ProtocolNodeProjectionEffect",
]
