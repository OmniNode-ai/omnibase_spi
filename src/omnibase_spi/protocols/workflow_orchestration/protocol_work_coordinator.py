"""
Protocol for Work Coordinator Service in ONEX Multi-Agent System.

This protocol defines the interface for coordinating work distribution,
agent assignment, and load balancing across multiple agents working on
parallel tickets with strict SPI purity compliance.
"""

from collections.abc import AsyncIterator
from datetime import datetime
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
        ProtocolWorkTicket,
    )


# Protocol-compatible literal types for coordination strategies
LiteralCoordinationStrategy = str
LiteralAgentSelectionCriteria = str
LiteralWorkDistributionMode = str


@runtime_checkable
class ProtocolWorkCoordinator(Protocol):
    """
    Protocol for work coordination and multi-agent management in ONEX systems.

    This protocol defines the interface for coordinating work distribution across
    multiple agents, managing agent lifecycles, and optimizing workload distribution
    with strict SPI purity compliance.

    Key Features:
        - Agent registration and lifecycle management
        - Dynamic work distribution and load balancing
        - Parallel execution coordination
        - Performance optimization and monitoring
        - Failure handling and work redistribution

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        coordinator: ProtocolWorkCoordinator = get_work_coordinator()

        # Initialize coordinator
        await coordinator.initialize_coordinator(
            agent_pool_size=10,
            coordination_strategy="load_balanced"
        )

        # Register agents
        await coordinator.register_agent(
            agent_id="agent-001",
            capabilities=["code_generation", "testing"],
            max_concurrent_work=3
        )

        # Distribute work
        tickets: list["ProtocolWorkTicket"] = create_work_tickets()
        assignments = await coordinator.distribute_work(
            tickets=tickets,
            distribution_mode="adaptive"
        )

        # Monitor coordination health
        health_status = await coordinator.monitor_coordination_health()
        ```
    """

    async def initialize_coordinator(
        self,
        agent_pool_size: int,
        coordination_strategy: LiteralCoordinationStrategy,
    ) -> bool:
        """
        Initialize the work coordinator with agent pool and strategy.

        Args:
            agent_pool_size: Maximum number of agents to coordinate
            coordination_strategy: Strategy for work coordination
                              (dependency_first, priority_weighted, load_balanced,
                               capability_optimized, round_robin)

        Returns:
            True if initialization was successful

        Raises:
            CoordinationError: If initialization fails
        """
        ...

    async def register_agent(
        self,
        agent_id: str,
        capabilities: list[str],
        max_concurrent_work: int | None = None,
    ) -> bool:
        """
        Register an agent with the coordination system.

        Args:
            agent_id: Unique identifier for the agent
            capabilities: List of agent capabilities/skills
            max_concurrent_work: Maximum concurrent work items for agent

        Returns:
            True if registration was successful

        Raises:
            RegistrationError: If agent registration fails
        """
        ...

    async def unregister_agent(self, agent_id: str, reason: str) -> bool:
        """
        Unregister an agent from the coordination system.

        Args:
            agent_id: ID of the agent to unregister
            reason: Reason for unregistration

        Returns:
            True if unregistration was successful

        Raises:
            UnregistrationError: If agent unregistration fails
        """
        ...

    async def distribute_work(
        self,
        tickets: list["ProtocolWorkTicket"],
        distribution_mode: LiteralWorkDistributionMode = "immediate",
    ) -> dict[str, list[str]]:
        """
        Distribute work tickets across available agents.

        Args:
            tickets: List of work tickets to distribute
            distribution_mode: How to distribute the work
                              (immediate, batched, scheduled, adaptive)

        Returns:
            Dictionary mapping agent IDs to assigned ticket IDs

        Raises:
            DistributionError: If work distribution fails
        """
        ...

    async def assign_ticket_to_agent(
        self,
        ticket_id: str,
        selection_criteria: LiteralAgentSelectionCriteria,
    ) -> str | None:
        """
        Assign a specific ticket to the best available agent.

        Args:
            ticket_id: ID of the ticket to assign
            selection_criteria: Criteria for selecting the agent
                              (least_loaded, best_capability_match, fastest_completion,
                               most_available, hybrid_scoring)

        Returns:
            Agent ID if assignment successful, None otherwise

        Raises:
            AssignmentError: If ticket assignment fails
        """
        ...

    async def reassign_work(
        self,
        from_agent_id: str,
        to_agent_id: str,
        ticket_ids: list[str],
    ) -> bool:
        """
        Reassign work from one agent to another.

        Args:
            from_agent_id: ID of the source agent
            to_agent_id: ID of the destination agent
            ticket_ids: List of ticket IDs to reassign

        Returns:
            True if reassignment was successful

        Raises:
            ReassignmentError: If work reassignment fails
        """
        ...

    async def balance_workload(self) -> dict[str, int]:
        """
        Balance workload across all active agents.

        Returns:
            Dictionary mapping agent IDs to new work counts

        Raises:
            BalancingError: If load balancing fails
        """
        ...

    async def get_agent_workload(self, agent_id: str) -> dict[str, int]:
        """
        Get current workload for a specific agent.

        Args:
            agent_id: ID of the agent

        Returns:
            Dictionary containing workload metrics

        Raises:
            AgentNotFoundError: If agent doesn't exist
        """
        ...

    async def get_optimal_agent_for_ticket(
        self,
        ticket: "ProtocolWorkTicket",
    ) -> str | None:
        """
        Find the optimal agent for a specific ticket.

        Args:
            ticket: Work ticket to find agent for

        Returns:
            Agent ID if optimal agent found, None otherwise
        """
        ...

    async def get_coordination_status(self) -> dict[str, str]:
        """
        Get current coordination system status.

        Returns:
            Dictionary containing coordination status information
        """
        ...

    async def pause_coordination(self, reason: str) -> bool:
        """
        Pause work coordination temporarily.

        Args:
            reason: Reason for pausing coordination

        Returns:
            True if coordination was paused successfully

        Raises:
            CoordinationError: If pausing fails
        """
        ...

    async def resume_coordination(self) -> bool:
        """
        Resume work coordination after pause.

        Returns:
            True if coordination was resumed successfully

        Raises:
            CoordinationError: If resuming fails
        """
        ...

    async def set_coordination_strategy(
        self, strategy: LiteralCoordinationStrategy
    ) -> bool:
        """
        Change the work coordination strategy.

        Args:
            strategy: New coordination strategy to use

        Returns:
            True if strategy was changed successfully

        Raises:
            ConfigurationError: If strategy change fails
        """
        ...

    async def get_coordination_strategy(self) -> LiteralCoordinationStrategy:
        """
        Get the current coordination strategy.

        Returns:
            Current coordination strategy
        """
        ...

    async def handle_agent_failure(
        self,
        agent_id: str,
        failure_reason: str,
    ) -> list[str]:
        """
        Handle agent failure and redistribute its work.

        Args:
            agent_id: ID of the failed agent
            failure_reason: Reason for the failure

        Returns:
            List of ticket IDs that were redistributed

        Raises:
            FailureHandlingError: If failure handling fails
        """
        ...

    async def get_work_distribution_metrics(self) -> dict[str, float]:
        """
        Get metrics about work distribution effectiveness.

        Returns:
            Dictionary containing distribution metrics
        """
        ...

    async def predict_completion_times(
        self,
        ticket_ids: list[str],
    ) -> dict[str, datetime | None]:
        """
        Predict completion times for given tickets.

        Args:
            ticket_ids: List of ticket IDs to predict for

        Returns:
            Dictionary mapping ticket IDs to predicted completion times
        """
        ...

    async def optimize_agent_assignments(self) -> dict[str, list[str]]:
        """
        Optimize current agent assignments for better performance.

        Returns:
            Dictionary of optimized assignments (agent_id -> ticket_ids)

        Raises:
            OptimizationError: If optimization fails
        """
        ...

    async def get_dependency_ready_work(self) -> list[str]:
        """
        Get work items that are ready based on dependency resolution.

        Returns:
            List of ticket IDs ready for assignment
        """
        ...

    async def coordinate_parallel_execution(
        self,
        max_parallel_agents: int | None = None,
    ) -> dict[str, list[str]]:
        """
        Coordinate parallel execution across multiple agents.

        Args:
            max_parallel_agents: Maximum number of agents to coordinate

        Returns:
            Dictionary mapping agent IDs to coordinated work assignments

        Raises:
            CoordinationError: If parallel coordination fails
        """
        ...

    async def monitor_coordination_health(self) -> dict[str, bool]:
        """
        Monitor the health of the coordination system.

        Returns:
            Dictionary containing health status indicators
        """
        ...

    async def get_agent_performance_scores(self) -> dict[str, float]:
        """
        Get performance scores for all registered agents.

        Returns:
            Dictionary mapping agent IDs to performance scores
        """
        ...

    async def subscribe_to_coordination_events(self) -> AsyncIterator[dict[str, str]]:
        """
        Subscribe to coordination system events.

        Yields:
            Coordination events as they occur

        Raises:
            SubscriptionError: If event subscription fails
        """
        ...

    async def create_work_batch(self, ticket_ids: list[str], batch_name: str) -> str:
        """
        Create a batch of related work items for coordinated execution.

        Args:
            ticket_ids: List of ticket IDs to include in batch
            batch_name: Name for the work batch

        Returns:
            Batch ID for the created batch

        Raises:
            BatchCreationError: If batch creation fails
        """
        ...

    async def execute_work_batch(self, batch_id: str) -> dict[str, str]:
        """
        Execute a previously created work batch.

        Args:
            batch_id: ID of the batch to execute

        Returns:
            Dictionary mapping ticket IDs to assigned agent IDs

        Raises:
            BatchExecutionError: If batch execution fails
        """
        ...

    async def get_coordination_statistics(self) -> dict[str, int]:
        """
        Get comprehensive coordination statistics.

        Returns:
            Dictionary containing coordination metrics and statistics
        """
        ...
