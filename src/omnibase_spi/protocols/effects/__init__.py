"""Effect execution protocols for omnibase_spi.

This module defines effect execution interfaces for the ONEX kernel:

- ``ProtocolEffect``: synchronous effect boundary (ordering guarantee)
- ``ProtocolPrimitiveEffectExecutor``: async primitive effects (kernel dispatch)
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
