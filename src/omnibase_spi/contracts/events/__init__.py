"""SPI event contracts — wire-format models for the three new event topics.

These contracts define the SPI-layer view of each event type.  They are
deliberately narrower than the corresponding Core models: the ``extensions``
field is the *only* extension channel.  No ad-hoc fields are permitted
(``extra="forbid"``).

Alignment invariant (enforced by ``test_contract_model_alignment.py``):
    SPI contract fields ⊆ Core model fields for each event type.

Exports:
    ContractGitHubPRStatusEvent: SPI contract for GitHub PR status events.
    ContractGitHookEvent: SPI contract for Git hook events.
    ContractLinearSnapshotEvent: SPI contract for Linear snapshot events.
"""

from omnibase_spi.contracts.events.contract_git_hook_event import ContractGitHookEvent
from omnibase_spi.contracts.events.contract_github_pr_status_event import (
    ContractGitHubPRStatusEvent,
)
from omnibase_spi.contracts.events.contract_linear_snapshot_event import (
    ContractLinearSnapshotEvent,
)

__all__ = [
    "ContractGitHubPRStatusEvent",
    "ContractGitHookEvent",
    "ContractLinearSnapshotEvent",
]
