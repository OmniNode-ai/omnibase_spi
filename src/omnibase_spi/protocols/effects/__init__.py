"""Effect execution protocols for omnibase_spi.

This module defines the primitive effect execution interface that enables
the ONEX kernel to execute effects without depending on handler implementations.
"""

from omnibase_spi.protocols.effects.protocol_primitive_effect_executor import (
    LiteralEffectCategory,
    LiteralEffectId,
    ProtocolPrimitiveEffectExecutor,
)

__all__ = [
    "LiteralEffectCategory",
    "LiteralEffectId",
    "ProtocolPrimitiveEffectExecutor",
]
