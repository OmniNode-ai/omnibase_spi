"""ContractGitHookEvent — SPI wire contract for Git hook events.

Topic: ``onex.evt.git.hook.v1``
Partition key: ``{repo}:{branch}``

This contract captures the result of a Git hook invocation (push,
pre-receive, post-receive, update, etc.) as observed by the hook
integration layer.  It is the SPI-layer view: a strict subset of
``ModelGitHookEvent`` from omnibase_core.

Design constraints:
    - ``extra="forbid"``: no undeclared fields permitted.
    - ``frozen=True``: instances are immutable after construction.
    - ``author`` captures the Git committer/pusher username (NOT email).
    - ``gates`` is a list of gate-name strings that were evaluated
      during the hook run.  Empty list means no gates were checked.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContractGitHookEvent(BaseModel):
    """SPI wire contract for a Git hook event.

    Published to ``onex.evt.git.hook.v1`` after a hook invocation completes.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        event_type: Must equal ``"onex.evt.git.hook.v1"``.
        hook: Hook name (e.g. ``"pre-commit"``, ``"post-receive"``).
        repo: Repository identifier (e.g. ``"OmniNode-ai/omniclaude"``).
        branch: Branch name the hook fired on.
        author: Git committer/pusher username (NOT email).
        outcome: Hook outcome — ``"pass"`` or ``"fail"``.
        gates: List of gate names evaluated during the hook run.
        extensions: Single extension channel for consumer-specific metadata.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    event_type: str = Field(
        default="onex.evt.git.hook.v1",
        description="Fully-qualified event type identifier; equals the topic name.",
    )
    hook: str = Field(
        ...,
        description="Hook name (e.g. 'pre-commit', 'post-receive').",
    )
    repo: str = Field(
        ...,
        description="Repository identifier (e.g. 'OmniNode-ai/omniclaude').",
    )
    branch: str = Field(
        ...,
        description="Branch name the hook fired on.",
    )
    author: str = Field(
        ...,
        description="Git committer/pusher username (NOT email).",
    )
    outcome: str = Field(
        ...,
        description="Hook outcome: 'pass' or 'fail'.",
    )
    gates: list[str] = Field(
        default_factory=list,
        description="Gate names evaluated during the hook run.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Single extension channel for consumer-specific metadata. "
            "Domain fields MUST NOT be embedded here."
        ),
    )
