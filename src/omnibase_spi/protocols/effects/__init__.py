"""Effect execution protocols for omnibase_spi.

This module defines:
- ``ProtocolEffect``: synchronous effect execution boundary (ordering guarantee)
- ``ProtocolPrimitiveEffectExecutor``: async primitive effect kernel
"""

from omnibase_spi.protocols.effects.protocol_effect import ProtocolEffect
from omnibase_spi.protocols.effects.protocol_primitive_effect_executor import (
    LiteralEffectCategory,
    LiteralEffectId,
    ProtocolPrimitiveEffectExecutor,
)

__all__ = [
    "LiteralEffectCategory",
    "LiteralEffectId",
    "ProtocolEffect",
    "ProtocolPrimitiveEffectExecutor",
]
