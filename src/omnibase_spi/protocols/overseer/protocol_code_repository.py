# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Overseer-specific code repository protocol.

Extends beyond ProtocolSourceControl with the full privileged action space
required by the overseer: push_branch, create_pr, admin_merge, force_push,
delete_branch, and rebase. Intended for overseer agents that need elevated
Git/GitHub operations beyond standard pipeline automation.
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
class ProtocolCodeRepository(Protocol):
    """Overseer-scoped code repository operations.

    Provides the full privileged action space needed by the overseer agent,
    including write operations (push_branch, create_pr), admin operations
    (admin_merge, force_push, delete_branch), and history operations (rebase).

    Implementors (e.g. AdapterCodeRepositoryGitHub) must authenticate with
    sufficient scope to perform all declared operations.

    Example:
        ```python
        repo: ProtocolCodeRepository = get_code_repository()

        await repo.connect()
        branch = await repo.push_branch("OmniNode-ai/omnibase_spi", "fix/foo", commits)
        pr = await repo.create_pr(
            "OmniNode-ai/omnibase_spi",
            title="fix: foo",
            body="…",
            head="fix/foo",
            base="main",
        )
        result = await repo.admin_merge("OmniNode-ai/omnibase_spi", pr.number)
        await repo.close()
        ```
    """

    # -- Lifecycle --

    async def connect(self) -> bool:
        """Establish a connection to the code repository service.

        Returns:
            True if connection was established successfully, False otherwise.
        """
        ...

    async def health_check(self) -> ProtocolServiceHealthStatus:
        """Check the health of the code repository service connection.

        Returns:
            Health status including service ID, status, and diagnostics.
        """
        ...

    async def get_capabilities(self) -> list[str]:
        """Discover capabilities supported by this adapter.

        Returns:
            List of capability identifiers such as ``["read", "write", "admin"]``.
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Release resources and close connections.

        Args:
            timeout_seconds: Maximum time to wait for cleanup.
        """
        ...

    # -- Read operations --

    async def get_pr(self, repo: str, pr_number: int) -> ModelPullRequest:
        """Retrieve a single pull request by number.

        Args:
            repo: Repository identifier (e.g. ``"OmniNode-ai/omnibase_spi"``).
            pr_number: Pull request number.

        Returns:
            Pull request model.

        Raises:
            KeyError: If PR is not found.
        """
        ...

    async def list_prs(
        self, repo: str, state: str = "open", limit: int = 50
    ) -> list[ModelPullRequest]:
        """List pull requests for a repository.

        Args:
            repo: Repository identifier.
            state: Filter by state — ``"open"``, ``"closed"``, or ``"all"``.
            limit: Maximum number of PRs to return.

        Returns:
            List of pull request models.
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

    # -- Write operations --

    async def push_branch(
        self,
        repo: str,
        branch_name: str,
        from_ref: str = "main",
    ) -> ModelBranch:
        """Create or update a branch in the remote repository.

        Args:
            repo: Repository identifier.
            branch_name: Name of the branch to create or force-update.
            from_ref: Ref to branch from (SHA, tag, or branch name).

        Returns:
            Branch metadata after the push.
        """
        ...

    async def create_pr(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        draft: bool = False,
    ) -> ModelPullRequest:
        """Open a pull request.

        Args:
            repo: Repository identifier.
            title: PR title.
            body: PR description body (markdown).
            head: Head branch name.
            base: Base branch to merge into.
            draft: Whether to open as a draft PR.

        Returns:
            Created pull request model.
        """
        ...

    # -- Admin operations --

    async def admin_merge(
        self,
        repo: str,
        pr_number: int,
        method: str = "squash",
    ) -> ModelMergeResult:
        """Merge a pull request with admin privileges, bypassing required reviews.

        Args:
            repo: Repository identifier.
            pr_number: Pull request number.
            method: Merge method — ``"merge"``, ``"squash"``, or ``"rebase"``.

        Returns:
            Merge result including SHA and status.

        Raises:
            ValueError: If the method is invalid or the PR is not mergeable.
        """
        ...

    async def force_push(
        self,
        repo: str,
        branch_name: str,
        target_ref: str,
    ) -> ModelBranch:
        """Force-push a branch to the specified ref.

        This operation rewrites remote history and should only be invoked by
        the overseer after explicit authorization.

        Args:
            repo: Repository identifier.
            branch_name: Branch to force-push.
            target_ref: SHA or ref to force the branch to.

        Returns:
            Updated branch metadata.
        """
        ...

    async def delete_branch(self, repo: str, branch_name: str) -> bool:
        """Delete a remote branch.

        Args:
            repo: Repository identifier.
            branch_name: Branch to delete.

        Returns:
            True if deletion succeeded, False if the branch did not exist.
        """
        ...

    async def rebase(
        self,
        repo: str,
        branch_name: str,
        onto: str = "main",
    ) -> ModelBranch:
        """Rebase a branch onto a target ref.

        Args:
            repo: Repository identifier.
            branch_name: Branch to rebase.
            onto: Target ref to rebase onto.

        Returns:
            Updated branch metadata after rebase.

        Raises:
            ValueError: If rebase fails due to conflicts.
        """
        ...
