# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for code hosting service integration.

Defines the standard interface for code hosting platforms (GitHub, GitLab, Bitbucket)
used by ONEX pipeline automation for PR management, branch operations, and CI status
queries.

RBAC:
    - read: Query PRs, branches, CI status, file contents
    - write: Create PRs, post comments, request reviews
    - admin: Merge PRs, delete branches, manage webhooks
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolCodeHost(Protocol):
    """Protocol for code hosting platform operations.

    Abstracts code hosting interactions across providers (GitHub, GitLab,
    Bitbucket) for use in ONEX CI/CD pipelines, agent-driven PR workflows,
    and automated code review.

    RBAC:
        - read: get_pull_request, list_pull_requests, get_ci_status, get_file_contents
        - write: create_pull_request, add_pr_comment, request_review
        - admin: merge_pull_request, delete_branch, configure_webhooks

    Example:
        ```python
        host: ProtocolCodeHost = get_code_host()

        pr_url = await host.create_pull_request(
            repo="OmniNode-ai/omnibase_spi",
            head="jonah/omn-7576-service-protocols",
            base="main",
            title="feat: add service lifecycle protocols",
            body="Defines ProtocolTicketService, ProtocolSecretStore, ProtocolCodeHost",
        )

        ci = await host.get_ci_status(repo="OmniNode-ai/omnibase_spi", ref="HEAD")
        if ci["state"] == "success":
            await host.merge_pull_request(
                repo="OmniNode-ai/omnibase_spi",
                pr_number=42,
                method="squash",
            )
        ```
    """

    async def create_pull_request(
        self,
        repo: str,
        head: str,
        base: str,
        title: str,
        body: str,
        labels: list[str] | None = None,
        reviewers: list[str] | None = None,
        metadata: dict[str, ContextValue] | None = None,
    ) -> str:
        """Create a pull request on the code hosting platform.

        Args:
            repo: Repository identifier (e.g., "OmniNode-ai/omnibase_spi")
            head: Source branch name
            base: Target branch name
            title: PR title
            body: PR description (markdown supported)
            labels: Optional labels to apply
            reviewers: Optional reviewer usernames to request
            metadata: Optional provider-specific metadata (draft, auto-merge, etc.)

        Returns:
            PR URL or identifier

        Raises:
            PermissionError: If caller lacks write RBAC role
            ValueError: If head or base branch does not exist
            ConnectionError: If service is unreachable
        """
        ...

    async def get_pull_request(
        self, repo: str, pr_number: int
    ) -> dict[str, ContextValue]:
        """Retrieve pull request details.

        Args:
            repo: Repository identifier
            pr_number: Pull request number

        Returns:
            PR data including title, body, status, checks, reviewers

        Raises:
            KeyError: If PR not found
            PermissionError: If caller lacks read RBAC role
        """
        ...

    async def merge_pull_request(
        self,
        repo: str,
        pr_number: int,
        method: str = "squash",
    ) -> bool:
        """Merge a pull request.

        Args:
            repo: Repository identifier
            pr_number: Pull request number
            method: Merge method ("merge", "squash", or "rebase")

        Returns:
            True if merge succeeded, False otherwise

        Raises:
            PermissionError: If caller lacks admin RBAC role
            ValueError: If PR is not mergeable or method is invalid
        """
        ...

    async def add_pr_comment(self, repo: str, pr_number: int, body: str) -> str:
        """Add a comment to a pull request.

        Args:
            repo: Repository identifier
            pr_number: Pull request number
            body: Comment body (markdown supported)

        Returns:
            Comment identifier

        Raises:
            KeyError: If PR not found
            PermissionError: If caller lacks write RBAC role
        """
        ...

    async def get_ci_status(self, repo: str, ref: str) -> dict[str, ContextValue]:
        """Get CI/check status for a git ref.

        Args:
            repo: Repository identifier
            ref: Git ref (branch name, tag, or SHA)

        Returns:
            CI status data including state, check runs, and conclusions

        Raises:
            KeyError: If ref not found
            PermissionError: If caller lacks read RBAC role
        """
        ...

    async def list_pull_requests(
        self,
        repo: str,
        state: str = "open",
        limit: int = 50,
    ) -> list[dict[str, ContextValue]]:
        """List pull requests for a repository.

        Args:
            repo: Repository identifier
            state: Filter by state ("open", "closed", "all")
            limit: Maximum number of PRs to return

        Returns:
            List of PR data dictionaries

        Raises:
            PermissionError: If caller lacks read RBAC role
        """
        ...

    async def health_check(self) -> bool:
        """Check if the code hosting service is reachable and healthy.

        Returns:
            True if service is healthy, False otherwise
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Release resources and close connections to the code host.

        Args:
            timeout_seconds: Maximum time to wait for cleanup.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If cleanup does not complete within the timeout.
        """
        ...
