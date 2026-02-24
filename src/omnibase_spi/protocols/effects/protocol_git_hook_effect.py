"""ProtocolGitHookEffect — SPI Protocol for Git hook event production.

Defines the abstract interface that the ONEX runtime calls when a Git
hook fires, producing an event to ``onex.evt.git.hook.v1``.

Architecture Context::

    [Git hook script (pre-commit / post-receive / …)]
          │
          ▼
    ProtocolGitHookEffect.emit(hook, repo, branch, author, outcome, gates)
          │ [async — serialises and queues the event]
          ▼
    [returns ContractGitHookEvent]
          │
          ▼
    [Runtime publishes to onex.evt.git.hook.v1]

Implementations MUST:
    - Be async (``emit()`` is an async method).
    - Return the ``ContractGitHookEvent`` that was produced.
    - Raise on unrecoverable serialisation or queuing errors.

Related:
    - OMN-2655: This ticket.
    - ContractGitHookEvent: Return type.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.events.contract_git_hook_event import (
        ContractGitHookEvent,
    )


@runtime_checkable
class ProtocolGitHookEffect(Protocol):
    """Async protocol for emitting Git hook events.

    Implementations serialise the hook invocation result into a
    ``ContractGitHookEvent`` and hand it to the runtime for Kafka
    publication on ``onex.evt.git.hook.v1``.

    Method Contract:
        ``emit(...)`` MUST:
        - Be async (``async def``).
        - Return the ``ContractGitHookEvent`` that was produced.
        - Raise ``RuntimeError`` on unrecoverable failure.

    isinstance Compliance:
        This protocol is ``@runtime_checkable``::

            assert isinstance(my_impl, ProtocolGitHookEffect)
    """

    async def emit(
        self,
        hook: str,
        repo: str,
        branch: str,
        author: str,
        outcome: str,
        gates: list[str] | None = None,
    ) -> ContractGitHookEvent:
        """Emit a Git hook event.

        Args:
            hook: Hook name (e.g. ``"pre-commit"``, ``"post-receive"``).
            repo: Repository identifier (e.g. ``"OmniNode-ai/omniclaude"``).
            branch: Branch name the hook fired on.
            author: Git committer/pusher username (NOT email).
            outcome: Hook outcome — ``"pass"`` or ``"fail"``.
            gates: Optional list of gate names evaluated during the hook run.

        Returns:
            The ``ContractGitHookEvent`` produced from the given parameters.

        Raises:
            RuntimeError: On unrecoverable serialisation or queuing errors.
        """
        ...
