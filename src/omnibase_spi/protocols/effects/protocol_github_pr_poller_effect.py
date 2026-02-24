"""ProtocolGitHubPRPollerEffect — SPI Protocol for GitHub PR status polling.

Defines the abstract interface that the ONEX runtime calls to poll GitHub
for pull-request triage state and produce events to
``onex.evt.github.pr-status.v1``.

Architecture Context::

    [Scheduler / Cron]
          │
          ▼
    ProtocolGitHubPRPollerEffect.poll(repo, pr_numbers)
          │ [async — may call GitHub REST/GraphQL API]
          ▼
    [returns list[ContractGitHubPRStatusEvent]]
          │
          ▼
    [Runtime publishes to onex.evt.github.pr-status.v1]

Implementations MUST:
    - Be async (``poll()`` is an async method).
    - Return one ``ContractGitHubPRStatusEvent`` per PR polled.
    - Raise on unrecoverable API errors rather than returning empty results
      for PRs that could not be polled.
    - NOT import from omnibase_core, omnibase_infra, or omniclaude.

Related:
    - OMN-2655: This ticket.
    - ContractGitHubPRStatusEvent: Return type per PR.
    - default_github_pr_poller.yaml: YAML handler contract for this protocol.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.events.contract_github_pr_status_event import (
        ContractGitHubPRStatusEvent,
    )


@runtime_checkable
class ProtocolGitHubPRPollerEffect(Protocol):
    """Async protocol for polling GitHub pull-request triage state.

    Implementations fetch the current triage state of one or more pull
    requests from the GitHub API and return a list of
    ``ContractGitHubPRStatusEvent`` instances ready for Kafka publication.

    Method Contract:
        ``poll(repo, pr_numbers)`` MUST:
        - Be async (``async def``).
        - Return one result per PR number requested.
        - Raise ``RuntimeError`` (or a subclass) on unrecoverable failure.
        - Be idempotent: re-polling the same PR at the same point in time
          MUST return the same triage state.

    isinstance Compliance:
        This protocol is ``@runtime_checkable``.  Implementations are checked
        at DI container registration time::

            assert isinstance(my_impl, ProtocolGitHubPRPollerEffect)

    Example Implementation::

        class GitHubRestPollerEffect:
            async def poll(
                self, repo: str, pr_numbers: list[int]
            ) -> list[ContractGitHubPRStatusEvent]:
                results = []
                for pr_num in pr_numbers:
                    data = await github_client.get_pr(repo, pr_num)
                    state = classify_triage_state(data)
                    results.append(
                        ContractGitHubPRStatusEvent(
                            repo=repo,
                            pr_number=pr_num,
                            triage_state=state,
                            title=data["title"],
                        )
                    )
                return results

        assert isinstance(GitHubRestPollerEffect(), ProtocolGitHubPRPollerEffect)
    """

    async def poll(
        self,
        repo: str,
        pr_numbers: list[int],
    ) -> list[ContractGitHubPRStatusEvent]:
        """Poll GitHub for the current triage state of the given pull requests.

        Args:
            repo: Repository identifier in ``{owner}/{name}`` format.
            pr_numbers: List of pull request numbers to poll.  Must be
                non-empty; passing an empty list is valid and returns ``[]``.

        Returns:
            One ``ContractGitHubPRStatusEvent`` per PR in ``pr_numbers``,
            in the same order.

        Raises:
            RuntimeError: On unrecoverable API errors (rate-limit exhausted,
                authentication failure, repo not found).
        """
        ...
