"""Effect node protocol definitions for omnibase_spi.

This package contains SPI-level effect node protocols used as
synchronous execution boundaries by the ONEX runtime.

Protocols:
    ProtocolNodeProjectionEffect: SPI protocol for synchronous projection write
        effect nodes. Concrete implementations (e.g. NodeProjectionEffect in
        omnibase_infra) satisfy this protocol.
"""

from omnibase_spi.effects.node_projection_effect import ProtocolNodeProjectionEffect

__all__ = [
    "ProtocolNodeProjectionEffect",
]
