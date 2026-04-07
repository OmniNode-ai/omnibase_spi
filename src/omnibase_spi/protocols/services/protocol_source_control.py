# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for source control service integration.

Defines the standard interface for source control platforms (GitHub, GitLab,
Bitbucket) used by ONEX pipeline automation for PR management, branch
operations, CI status queries, and diff retrieval.

This protocol is a structural subtype of ProtocolExternalService — it
repeats the lifecycle signatures rather than inheriting, which is how
Python Protocols achieve structural subtyping.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.services.contract_source_control_types import (
        ModelBranch,
        ModelCIStatus,
        ModelDiff,
        ModelMergeResult,
        ModelPullRequest,
    )
    from omnibase_spi.protocols.types.protocol_service_types import (
        ProtocolServiceHealthStatus,
    )


@runtime_checkable
class ProtocolSourceControl(Protocol):
    """Protocol for source control platform operations.

    Abstracts source control interactions across providers (GitHub, GitLab,
    Bitbucket) for use in ONEX CI/CD pipelines, agent-driven PR workflows,
    and automated code review.

    This is a structural subtype of ProtocolExternalService — any object
    satisfying this protocol also satisfies ProtocolExternalService.

    Example:
        ```python
        sc: ProtocolSourceControl = get_source_control()

        connected = await sc.connect()
        if connected:
            prs = await sc.list_prs("OmniNode-ai/omnibase_spi", state="open")
            for pr in prs:
                ci = await sc.get_ci_status("OmniNode-ai/omnibase_spi", pr.head_ref)
                if ci.state == "success":
                    await sc.merge_pr("OmniNode-ai/omnibase_spi", pr.number)

        await sc.close()
        ```
    """

    # -- Lifecycle (structural subtype of ProtocolExternalService) --

    async def connect(self) -> bool:
        """Establish a connection to the source control service.

        Returns:
            True if connection was established successfully, False otherwise.
        """
        ...

    async def health_check(self) -> ProtocolServiceHealthStatus:
        """Check the health of the source control service connection.

        Returns:
            Health status including service ID, status, and diagnostics.
        """
        ...

    async def get_capabilities(self) -> list[str]:
        """Discover capabilities supported by this source control adapter.

        Returns:
            List of capability identifiers (e.g., ``["read", "write", "admin"]``).
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Release resources and close connections.

        Args:
            timeout_seconds: Maximum time to wait for cleanup.
        """
        ...

    # -- Domain operations --

    async def list_prs(
        self, repo: str, state: str = "open", limit: int = 50
    ) -> list[ModelPullRequest]:
        """List pull requests for a repository.

        Args:
            repo: Repository identifier (e.g., "OmniNode-ai/omnibase_spi").
            state: Filter by state ("open", "closed", "all").
            limit: Maximum number of PRs to return.

        Returns:
            List of pull request models.
        """
        ...

    async def get_pr(self, repo: str, pr_number: int) -> ModelPullRequest:
        """Retrieve a single pull request by number.

        Args:
            repo: Repository identifier.
            pr_number: Pull request number.

        Returns:
            Pull request model.

        Raises:
            KeyError: If PR not found.
        """
        ...

    async def merge_pr(
        self, repo: str, pr_number: int, method: str = "squash"
    ) -> ModelMergeResult:
        """Merge a pull request.

        Args:
            repo: Repository identifier.
            pr_number: Pull request number.
            method: Merge method ("merge", "squash", or "rebase").

        Returns:
            Merge result including SHA and status.

        Raises:
            ValueError: If PR is not mergeable or method is invalid.
        """
        ...

    async def get_ci_status(self, repo: str, ref: str) -> ModelCIStatus:
        """Get CI/check status for a git ref.

        Args:
            repo: Repository identifier.
            ref: Git ref (branch name, tag, or SHA).

        Returns:
            CI status with state and individual check runs.
        """
        ...

    async def create_branch(
        self, repo: str, branch_name: str, from_ref: str = "main"
    ) -> ModelBranch:
        """Create a new branch.

        Args:
            repo: Repository identifier.
            branch_name: Name for the new branch.
            from_ref: Ref to branch from.

        Returns:
            Branch metadata.
        """
        ...

    async def get_diff(self, repo: str, base: str, head: str) -> ModelDiff:
        """Get the diff between two refs.

        Args:
            repo: Repository identifier.
            base: Base ref.
            head: Head ref.

        Returns:
            Diff summary with file counts and patch text.
        """
        ...

    async def enable_auto_merge(self, repo: str, pr_number: int) -> bool:
        """Enable auto-merge on a pull request.

        Args:
            repo: Repository identifier.
            pr_number: Pull request number.

        Returns:
            True if auto-merge was enabled successfully.
        """
        ...
