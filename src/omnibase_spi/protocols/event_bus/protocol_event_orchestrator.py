"""
Protocol for Event Orchestration in ONEX distributed systems.

This protocol defines the interface for coordinating events between
distributed services with proper SPI purity and type safety.
"""

from collections.abc import AsyncIterator
from datetime import datetime
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_event_bus_types import (
        ProtocolAgentEvent,
        ProtocolEventBusAgentStatus,
        ProtocolEventBusSystemEvent,
        ProtocolProgressUpdate,
        ProtocolWorkResult,
    )
    from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
        ProtocolWorkTicket,
    )


@runtime_checkable
class ProtocolEventOrchestrator(Protocol):
    """
    Protocol for event orchestration and workflow coordination in ONEX systems.

    This protocol defines the interface for coordinating events between distributed
    services, managing agent lifecycle, and handling work distribution with strict
    SPI purity compliance.

    Key Features:
        - Agent lifecycle management (spawn, terminate, health monitoring)
        - Work ticket assignment and load balancing
        - Event-driven coordination with async patterns
        - Comprehensive error handling and recovery
        - Performance metrics and monitoring

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        orchestrator: ProtocolEventOrchestrator = get_orchestrator()

        # Handle work ticket creation
        ticket: "ProtocolWorkTicket" = create_work_ticket()
        success = await orchestrator.handle_work_ticket_created(ticket)

        # Monitor agent health
        health_status = await orchestrator.monitor_agent_health()
        for agent_id, status in health_status.items():
            print(f"Agent {agent_id}: {status}")

        # Subscribe to orchestration events
        async for event in orchestrator.subscribe_to_orchestration_events():
            print(f"Event: {event.event_type}")
        ```
    """

    async def handle_work_ticket_created(self, ticket: "ProtocolWorkTicket") -> bool:
        """
        Handle work ticket creation event and initiate assignment process.

        Args:
            ticket: Work ticket that was created

        Returns:
            True if handling was successful

        Raises:
            OrchestrationError: If handling fails
        """
        ...

    async def assign_work_to_agent(
        self,
        ticket: "ProtocolWorkTicket",
        agent_id: str | None = None,
    ) -> str:
        """
        Assign work ticket to an available agent.

        Args:
            ticket: Work ticket to assign
            agent_id: Optional specific agent ID, otherwise auto-select

        Returns:
            ID of the agent assigned to the work

        Raises:
            NoAvailableAgentsError: If no agents are available
            AgentNotFoundError: If specified agent is not found
            AssignmentError: If assignment fails
        """
        ...

    async def handle_agent_progress_update(
        self, update: "ProtocolProgressUpdate"
    ) -> bool:
        """
        Handle progress update from agent and broadcast to interested parties.

        Args:
            update: Progress update from agent

        Returns:
            True if handling was successful

        Raises:
            OrchestrationError: If handling fails
        """
        ...

    async def handle_work_completion(self, result: "ProtocolWorkResult") -> bool:
        """
        Handle work completion and perform post-completion tasks.

        Args:
            result: Work completion result from agent

        Returns:
            True if handling was successful

        Raises:
            OrchestrationError: If handling fails
        """
        ...

    async def handle_agent_error(self, error_event: "ProtocolAgentEvent") -> bool:
        """
        Handle agent error events and perform recovery actions.

        Args:
            error_event: Error event from agent

        Returns:
            True if handling was successful

        Raises:
            OrchestrationError: If handling fails
        """
        ...

    async def monitor_agent_health(self) -> dict[str, "ProtocolEventBusAgentStatus"]:
        """
        Monitor health of all active agents.

        Returns:
            Dictionary mapping agent IDs to their status
        """
        ...

    async def rebalance_workload(self) -> bool:
        """
        Rebalance workload across available agents.

        Returns:
            True if rebalancing was performed

        Raises:
            OrchestrationError: If rebalancing fails
        """
        ...

    async def handle_agent_spawn_request(self, agent_config_template: str) -> str:
        """
        Handle request to spawn new agent and configure it.

        Args:
            agent_config_template: Template name for agent configuration

        Returns:
            ID of the newly spawned agent

        Raises:
            SpawnError: If agent spawning fails
            ConfigurationError: If configuration fails
        """
        ...

    async def handle_agent_termination_request(
        self,
        agent_id: str,
        reason: str,
    ) -> bool:
        """
        Handle request to terminate agent and clean up resources.

        Args:
            agent_id: ID of agent to terminate
            reason: Reason for termination

        Returns:
            True if termination was successful

        Raises:
            TerminationError: If termination fails
        """
        ...

    async def get_workflow_metrics(self) -> dict[str, float]:
        """
        Get workflow performance metrics.

        Returns:
            Dictionary of workflow metrics including throughput, latency, error rates
        """
        ...

    async def subscribe_to_orchestration_events(
        self,
    ) -> AsyncIterator["ProtocolEventBusSystemEvent"]:
        """
        Subscribe to orchestration events for monitoring.

        Yields:
            Orchestration events as they occur

        Raises:
            SubscriptionError: If subscription fails
        """
        ...

    async def handle_ticket_priority_change(
        self,
        ticket_id: str,
        new_priority: str,
    ) -> bool:
        """
        Handle change in work ticket priority and adjust scheduling.

        Args:
            ticket_id: ID of the ticket with priority change
            new_priority: New priority level

        Returns:
            True if handling was successful

        Raises:
            OrchestrationError: If handling fails
        """
        ...

    async def handle_agent_capacity_change(
        self,
        agent_id: str,
        new_capacity: int,
    ) -> bool:
        """
        Handle change in agent capacity and adjust workload distribution.

        Args:
            agent_id: ID of the agent with capacity change
            new_capacity: New capacity limit

        Returns:
            True if handling was successful

        Raises:
            OrchestrationError: If handling fails
        """
        ...

    async def pause_agent_operations(self, agent_id: str) -> bool:
        """
        Pause operations for a specific agent.

        Args:
            agent_id: ID of agent to pause

        Returns:
            True if pause was successful

        Raises:
            OrchestrationError: If pause fails
        """
        ...

    async def resume_agent_operations(self, agent_id: str) -> bool:
        """
        Resume operations for a paused agent.

        Args:
            agent_id: ID of agent to resume

        Returns:
            True if resume was successful

        Raises:
            OrchestrationError: If resume fails
        """
        ...

    async def get_pending_work_queue(self) -> list["ProtocolWorkTicket"]:
        """
        Get list of pending work tickets in the queue.

        Returns:
            List of pending work tickets ordered by priority
        """
        ...

    async def get_active_work_assignments(self) -> dict[str, list[str]]:
        """
        Get current work assignments for all agents.

        Returns:
            Dictionary mapping agent IDs to lists of assigned ticket IDs
        """
        ...

    async def estimate_completion_time(
        self,
        ticket: "ProtocolWorkTicket",
    ) -> datetime | None:
        """
        Estimate completion time for a work ticket.

        Args:
            ticket: Work ticket to estimate completion for

        Returns:
            Estimated completion datetime or None if cannot estimate
        """
        ...

    async def handle_dependency_resolution(
        self,
        ticket_id: str,
        dependency_ticket_id: str,
    ) -> bool:
        """
        Handle resolution of work ticket dependencies.

        Args:
            ticket_id: ID of ticket waiting for dependency
            dependency_ticket_id: ID of dependency ticket that was resolved

        Returns:
            True if handling was successful

        Raises:
            OrchestrationError: If handling fails
        """
        ...

    async def create_orchestration_report(self) -> dict[str, str]:
        """
        Create comprehensive orchestration status report.

        Returns:
            Dictionary containing orchestration status and metrics
        """
        ...

    async def handle_emergency_shutdown(self, reason: str) -> bool:
        """
        Handle emergency shutdown of the orchestration system.

        Args:
            reason: Reason for emergency shutdown

        Returns:
            True if shutdown was successful

        Raises:
            ShutdownError: If shutdown fails
        """
        ...
