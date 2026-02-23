"""ContractGitHubPRStatusEvent — SPI wire contract for GitHub PR status events.

Topic: ``onex.evt.github.pr-status.v1``
Partition key: ``{repo}:{pr_number}``

This contract captures the triage state of a GitHub pull request as polled
by ``ProtocolGitHubPRPollerEffect``.  It is the SPI-layer view: a strict
subset of ``ModelGitHubPRStatusEvent`` from omnibase_core.

Design constraints:
    - ``extra="forbid"``: no undeclared fields permitted; all extensibility
      goes through the single ``extensions`` channel.
    - ``frozen=True``: instances are immutable after construction.
    - ``repo`` MUST follow ``{owner}/{name}`` format (e.g. ``OmniNode-ai/omniclaude``).
    - ``triage_state`` is limited to the 8 canonical states shared with
      ``ModelGitHubPRStatusEvent``.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

TriageState = Literal[
    "draft",
    "stale",
    "ci_failing",
    "changes_requested",
    "ready_to_merge",
    "approved_pending_ci",
    "needs_review",
    "blocked",
]


class ContractGitHubPRStatusEvent(BaseModel):
    """SPI wire contract for a GitHub PR status event.

    Produced by ``ProtocolGitHubPRPollerEffect.poll()`` and published to
    ``onex.evt.github.pr-status.v1``.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        event_type: Must equal ``"onex.evt.github.pr-status.v1"``.
        repo: Repository identifier in ``{owner}/{name}`` format.
        pr_number: Pull request number (positive integer).
        triage_state: Current triage classification of the PR.
        title: PR title (may be empty string if not fetched).
        extensions: Single extension channel for consumer-specific metadata.
            All keys must be strings; values are arbitrary JSON-compatible
            types.  Producers MUST NOT embed domain fields here that belong
            on the model itself.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    event_type: str = Field(
        default="onex.evt.github.pr-status.v1",
        description="Fully-qualified event type identifier; equals the topic name.",
    )
    repo: str = Field(
        ...,
        description=(
            "Repository in '{owner}/{name}' format "
            "(e.g. 'OmniNode-ai/omniclaude')."
        ),
    )
    pr_number: int = Field(
        ...,
        ge=1,
        description="Pull request number.",
    )
    triage_state: TriageState = Field(
        ...,
        description="Current triage classification of the pull request.",
    )
    title: str = Field(
        default="",
        description="Pull request title.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Single extension channel for consumer-specific metadata. "
            "Domain fields MUST NOT be embedded here."
        ),
    )
