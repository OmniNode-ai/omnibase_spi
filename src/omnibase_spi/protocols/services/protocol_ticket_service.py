# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for ticket/issue tracking service integration.

Defines the standard interface for ticket tracking systems (Linear, Jira, GitHub Issues)
used by ONEX pipeline automation for ticket creation, status updates, and querying.

RBAC:
    - read: Query tickets, list statuses, search
    - write: Create tickets, update status, add comments
    - admin: Delete tickets, manage labels/workflows
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolTicketService(Protocol):
    """Protocol for ticket/issue tracking service operations.

    Abstracts ticket lifecycle management across providers (Linear, Jira,
    GitHub Issues) for use in ONEX pipeline automation, agent orchestration,
    and compliance tracking.

    RBAC:
        - read: get_ticket, list_tickets, get_ticket_status, search_tickets
        - write: create_ticket, update_ticket_status, add_comment
        - admin: delete_ticket, configure_workflows

    Example:
        ```python
        service: ProtocolTicketService = get_ticket_service()

        ticket_id = await service.create_ticket(
            title="Fix auth middleware",
            description="Session tokens non-compliant",
            labels=["bug", "security"],
            metadata={"priority": "high", "team": "platform"},
        )

        await service.update_ticket_status(ticket_id, "in_progress")
        await service.add_comment(ticket_id, "PR opened: #1234")
        ```
    """

    async def create_ticket(
        self,
        title: str,
        description: str,
        labels: list[str] | None = None,
        assignee: str | None = None,
        metadata: dict[str, ContextValue] | None = None,
    ) -> str:
        """Create a new ticket in the tracking system.

        Args:
            title: Ticket title/summary
            description: Detailed description (markdown supported)
            labels: Optional labels/tags to apply
            assignee: Optional assignee identifier
            metadata: Optional provider-specific metadata (priority, team, etc.)

        Returns:
            Ticket identifier (e.g., "OMN-1234", "PROJ-567")

        Raises:
            PermissionError: If caller lacks write RBAC role
            ConnectionError: If service is unreachable
        """
        ...

    async def get_ticket(self, ticket_id: str) -> dict[str, ContextValue]:
        """Retrieve ticket details by identifier.

        Args:
            ticket_id: Ticket identifier

        Returns:
            Ticket data including title, description, status, assignee, labels

        Raises:
            KeyError: If ticket not found
            PermissionError: If caller lacks read RBAC role
        """
        ...

    async def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        """Update the status of an existing ticket.

        Args:
            ticket_id: Ticket identifier
            status: New status value (e.g., "in_progress", "done", "cancelled")

        Returns:
            True if update succeeded, False otherwise

        Raises:
            KeyError: If ticket not found
            ValueError: If status is not a valid transition
            PermissionError: If caller lacks write RBAC role
        """
        ...

    async def add_comment(self, ticket_id: str, body: str) -> str:
        """Add a comment to an existing ticket.

        Args:
            ticket_id: Ticket identifier
            body: Comment body (markdown supported)

        Returns:
            Comment identifier

        Raises:
            KeyError: If ticket not found
            PermissionError: If caller lacks write RBAC role
        """
        ...

    async def list_tickets(
        self,
        filters: dict[str, ContextValue] | None = None,
        limit: int = 50,
    ) -> list[dict[str, ContextValue]]:
        """List tickets matching optional filters.

        Args:
            filters: Optional filter criteria (status, assignee, labels, etc.)
            limit: Maximum number of tickets to return

        Returns:
            List of ticket data dictionaries

        Raises:
            PermissionError: If caller lacks read RBAC role
        """
        ...

    async def get_ticket_status(self, ticket_id: str) -> str:
        """Get the current status of a ticket.

        Args:
            ticket_id: Ticket identifier

        Returns:
            Current status string

        Raises:
            KeyError: If ticket not found
            PermissionError: If caller lacks read RBAC role
        """
        ...

    async def health_check(self) -> bool:
        """Check if the ticket service is reachable and healthy.

        Returns:
            True if service is healthy, False otherwise
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Release resources and close connections to the ticket service.

        Args:
            timeout_seconds: Maximum time to wait for cleanup.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If cleanup does not complete within the timeout.
        """
        ...
