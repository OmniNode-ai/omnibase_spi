# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for project tracking service integration.

Defines the standard interface for project tracking systems (Linear, Jira,
GitHub Issues) used by ONEX pipeline automation for issue management,
search, and project-level operations.

This protocol succeeds ProtocolTicketService with typed return models,
``search_issues``, and project-level operations. ProtocolTicketService
remains available during transition but is deprecated.

This protocol is a structural subtype of ProtocolExternalService.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.services.contract_project_tracker_types import (
        ModelComment,
        ModelIssue,
        ModelProject,
    )
    from omnibase_spi.protocols.types.protocol_service_types import (
        ProtocolServiceHealthStatus,
    )


@runtime_checkable
class ProtocolProjectTracker(Protocol):
    """Protocol for project tracking platform operations.

    Abstracts issue/ticket lifecycle management across providers (Linear,
    Jira, GitHub Issues) for use in ONEX pipeline automation, agent
    orchestration, and compliance tracking.

    This is a structural subtype of ProtocolExternalService — any object
    satisfying this protocol also satisfies ProtocolExternalService.

    Example:
        ```python
        tracker: ProtocolProjectTracker = get_project_tracker()

        connected = await tracker.connect()
        if connected:
            issues = await tracker.search_issues("auth middleware", limit=10)
            for issue in issues:
                print(f"{issue.identifier}: {issue.title} [{issue.state}]")

        await tracker.close()
        ```
    """

    # -- Lifecycle (structural subtype of ProtocolExternalService) --

    async def connect(self) -> bool:
        """Establish a connection to the project tracking service.

        Returns:
            True if connection was established successfully, False otherwise.
        """
        ...

    async def health_check(self) -> ProtocolServiceHealthStatus:
        """Check the health of the project tracking service connection.

        Returns:
            Health status including service ID, status, and diagnostics.
        """
        ...

    async def get_capabilities(self) -> list[str]:
        """Discover capabilities supported by this project tracker adapter.

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

    async def list_issues(
        self, filters: dict[str, str] | None = None, limit: int = 50
    ) -> list[ModelIssue]:
        """List issues matching optional filters.

        Args:
            filters: Optional filter criteria (state, assignee, labels, etc.).
            limit: Maximum number of issues to return.

        Returns:
            List of issue models.
        """
        ...

    async def get_issue(self, issue_id: str) -> ModelIssue:
        """Retrieve a single issue by identifier.

        Args:
            issue_id: Issue identifier (e.g., "internal issue" or internal UUID).

        Returns:
            Issue model.

        Raises:
            KeyError: If issue not found.
        """
        ...

    async def create_issue(
        self,
        title: str,
        description: str,
        labels: list[str] | None = None,
        assignee: str | None = None,
        priority: str | None = None,
        team: str | None = None,
    ) -> ModelIssue:
        """Create a new issue in the project tracker.

        Args:
            title: Issue title.
            description: Issue description (markdown supported).
            labels: Optional labels to apply.
            assignee: Optional assignee identifier.
            priority: Optional priority level.
            team: Optional team identifier.

        Returns:
            The created issue model.
        """
        ...

    async def update_issue(self, issue_id: str, updates: dict[str, str]) -> ModelIssue:
        """Update fields on an existing issue.

        Args:
            issue_id: Issue identifier.
            updates: Key-value pairs of fields to update.

        Returns:
            The updated issue model.

        Raises:
            KeyError: If issue not found.
        """
        ...

    async def search_issues(self, query: str, limit: int = 50) -> list[ModelIssue]:
        """Search issues by text query.

        Args:
            query: Search query string.
            limit: Maximum number of results.

        Returns:
            List of matching issue models.
        """
        ...

    async def add_comment(self, issue_id: str, body: str) -> ModelComment:
        """Add a comment to an issue.

        Args:
            issue_id: Issue identifier.
            body: Comment body (markdown supported).

        Returns:
            The created comment model.

        Raises:
            KeyError: If issue not found.
        """
        ...

    async def get_project(self, project_id: str) -> ModelProject:
        """Retrieve a project by identifier.

        Args:
            project_id: Project identifier.

        Returns:
            Project model.

        Raises:
            KeyError: If project not found.
        """
        ...

    async def list_projects(self, limit: int = 50) -> list[ModelProject]:
        """List projects accessible to the current user.

        Args:
            limit: Maximum number of projects to return.

        Returns:
            List of project models.
        """
        ...
