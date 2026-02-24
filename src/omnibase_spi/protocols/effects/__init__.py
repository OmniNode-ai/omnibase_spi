"""Effect execution protocols for omnibase_spi.

This module defines effect execution interfaces for the ONEX kernel:

- ``ProtocolEffect``: synchronous effect boundary (ordering guarantee)
- ``ProtocolPrimitiveEffectExecutor``: async primitive effects (kernel dispatch)
- ``ProtocolGitHubPRPollerEffect``: GitHub PR triage state poller (OMN-2655)
- ``ProtocolGitHookEffect``: Git hook event emitter (OMN-2655)
- ``ProtocolLinearSnapshotEffect``: Linear workspace snapshot poller (OMN-2655)
"""

from omnibase_spi.protocols.effects.protocol_effect import ProtocolEffect
from omnibase_spi.protocols.effects.protocol_git_hook_effect import (
    ProtocolGitHookEffect,
)
from omnibase_spi.protocols.effects.protocol_github_pr_poller_effect import (
    ProtocolGitHubPRPollerEffect,
)
from omnibase_spi.protocols.effects.protocol_linear_snapshot_effect import (
    ProtocolLinearSnapshotEffect,
)
from omnibase_spi.protocols.effects.protocol_primitive_effect_executor import (
    LiteralEffectCategory,
    LiteralEffectId,
    ProtocolPrimitiveEffectExecutor,
)

__all__ = [
    "LiteralEffectCategory",
    "LiteralEffectId",
    "ProtocolEffect",
    "ProtocolGitHookEffect",
    "ProtocolGitHubPRPollerEffect",
    "ProtocolLinearSnapshotEffect",
    "ProtocolPrimitiveEffectExecutor",
]
