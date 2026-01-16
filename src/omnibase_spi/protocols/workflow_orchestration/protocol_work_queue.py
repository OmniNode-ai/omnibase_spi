"""
Protocol for Work Queue Integration with ONEX Work Ticket System.

This protocol defines the interface for integrating Claude Code agents
with the ONEX work ticket infrastructure, enabling seamless ticket
assignment, processing, and status synchronization.
"""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue
from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
    ProtocolWorkTicket,
)

if TYPE_CHECKING:
    from omnibase_core.types import JsonType

LiteralWorkQueuePriority = Literal["urgent", "high", "normal", "low", "deferred"]
LiteralAssignmentStrategy = Literal[
    "round_robin",
    "least_loaded",
    "capability_based",
    "priority_weighted",
    "dependency_optimized",
]


@runtime_checkable
class ProtocolWorkQueue(Protocol):
    """
    Protocol for work queue integration with ONEX work ticket system.

    Provides comprehensive work queue management including ticket lifecycle,
    dependency tracking, assignment strategies, and checkpoint management
    for coordinated multi-agent work execution.

    Example:
        ```python
        queue: ProtocolWorkQueue = get_work_queue()

        # Connect to work system
        await queue.connect_to_work_system()

        # Fetch and assign tickets
        tickets = await queue.fetch_pending_tickets(limit=10)
        for ticket in tickets:
            await queue.assign_ticket_to_agent(ticket.id, "agent-001")

        # Track progress
        await queue.update_ticket_progress("ticket-123", 0.5)

        # Handle completion
        await queue.complete_ticket("ticket-123", {"output": "result"})

        # Or handle failure
        await queue.fail_ticket("ticket-456", "Processing error")

        # Manage dependencies
        deps = await queue.get_ticket_dependencies("ticket-789")
        ready = await queue.get_ready_tickets()

        # Get statistics
        stats = await queue.get_queue_statistics()
        print(f"Pending: {stats['pending']}, In-Progress: {stats['in_progress']}")
        ```

    See Also:
        - ProtocolWorkCoordinator: High-level coordination
        - ProtocolWorkTicket: Ticket structure
        - ProtocolWorkflowEventBus: Event-based coordination
    """

    async def connect_to_work_system(self) -> bool: ...

    async def fetch_pending_tickets(
        self, limit: int | None = None
    ) -> list[ProtocolWorkTicket]: ...

    async def subscribe_to_ticket_updates(
        self,
    ) -> AsyncIterator[ProtocolWorkTicket]: ...

    async def assign_ticket_to_agent(
        self, ticket_id: str, agent_id: str
    ) -> ProtocolWorkTicket: ...

    async def update_ticket_status(
        self, ticket_id: str, status: str, message: str | None = None
    ) -> bool: ...

    async def update_ticket_progress(
        self, ticket_id: str, progress_percent: float
    ) -> bool: ...

    async def complete_ticket(
        self, ticket_id: str, result_data: dict[str, "ContextValue"]
    ) -> bool: ...

    async def fail_ticket(self, ticket_id: str, error_message: str) -> bool: ...

    async def get_ticket_by_id(self, ticket_id: str) -> ProtocolWorkTicket | None: ...

    async def get_tickets_by_priority(
        self, priority: LiteralWorkQueuePriority
    ) -> list[ProtocolWorkTicket]: ...

    async def get_tickets_by_agent(self, agent_id: str) -> list[ProtocolWorkTicket]: ...

    async def get_available_tickets(
        self,
        agent_capabilities: list[str] | None = None,
        max_priority: "LiteralWorkQueuePriority | None" = None,
    ) -> list[ProtocolWorkTicket]: ...

    async def reserve_ticket(
        self, ticket_id: str, agent_id: str, duration_minutes: int
    ) -> bool: ...

    async def release_ticket_reservation(
        self, ticket_id: str, agent_id: str
    ) -> bool: ...

    async def get_queue_statistics(self) -> dict[str, int]: ...

    async def get_ticket_dependencies(self, ticket_id: str) -> list[str]: ...

    async def add_ticket_dependency(
        self, ticket_id: str, dependency_ticket_id: str
    ) -> bool: ...

    async def remove_ticket_dependency(
        self, ticket_id: str, dependency_ticket_id: str
    ) -> bool: ...

    async def get_blocked_tickets(self) -> list[ProtocolWorkTicket]: ...

    async def get_ready_tickets(self) -> list[ProtocolWorkTicket]: ...

    async def set_assignment_strategy(
        self, strategy: LiteralAssignmentStrategy
    ) -> bool: ...

    async def get_assignment_strategy(self) -> "LiteralAssignmentStrategy": ...

    async def requeue_ticket(self, ticket_id: str, reason: str) -> bool: ...

    async def estimate_completion_time(self, ticket_id: str) -> "JsonType": ...

    async def get_ticket_metrics(self, ticket_id: str) -> dict[str, float]: ...

    async def create_ticket_checkpoint(
        self, ticket_id: str, checkpoint_data: dict[str, "ContextValue"]
    ) -> str: ...

    async def restore_ticket_checkpoint(
        self, ticket_id: str, checkpoint_id: str
    ) -> bool: ...
