"""
Protocol for Work Queue Integration with ONEX Work Ticket System.

This protocol defines the interface for integrating Claude Code agents
with the ONEX work ticket infrastructure, enabling seamless ticket
assignment, processing, and status synchronization.
"""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, Literal, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue

if TYPE_CHECKING:
    pass
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
    """Protocol for work queue integration and ticket management."""

    async def connect_to_work_system(self) -> bool: ...

    async def fetch_pending_tickets(self, limit: int | None = None) -> list[Any]: ...

    async def subscribe_to_ticket_updates(self) -> AsyncIterator[Any]: ...

    async def assign_ticket_to_agent(self, ticket_id: str, agent_id: str) -> Any: ...

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

    async def get_ticket_by_id(self, ticket_id: str) -> Any | None: ...

    async def get_tickets_by_priority(
        self, priority: LiteralWorkQueuePriority
    ) -> list[Any]: ...

    async def get_tickets_by_agent(self, agent_id: str) -> list[Any]: ...

    async def get_available_tickets(
        self,
        agent_capabilities: list[str] | None = None,
        max_priority: "LiteralWorkQueuePriority | None" = None,
    ) -> list[Any]: ...

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

    async def get_blocked_tickets(self) -> list[Any]: ...

    async def get_ready_tickets(self) -> list[Any]: ...

    async def set_assignment_strategy(
        self, strategy: LiteralAssignmentStrategy
    ) -> bool: ...

    async def get_assignment_strategy(self) -> "LiteralAssignmentStrategy": ...

    async def requeue_ticket(self, ticket_id: str, reason: str) -> bool: ...

    async def estimate_completion_time(self, ticket_id: str) -> Any: ...

    async def get_ticket_metrics(self, ticket_id: str) -> dict[str, float]: ...

    async def create_ticket_checkpoint(
        self, ticket_id: str, checkpoint_data: dict[str, "ContextValue"]
    ) -> str: ...

    async def restore_ticket_checkpoint(
        self, ticket_id: str, checkpoint_id: str
    ) -> bool: ...
