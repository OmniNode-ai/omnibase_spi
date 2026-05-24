# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Protocol definition for Direct Knowledge Pipeline Service.

This protocol defines the interface for services that bypass the repository
and write directly to PostgreSQL for debug logs, velocity tracking, PR descriptions,
and agent actions using strong typing throughout.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_advanced_types import (
        ProtocolAgentAction,
        ProtocolAgentDebugIntelligence,
        ProtocolAIExecutionMetrics,
        ProtocolPRTicket,
        ProtocolVelocityLog,
    )
    from omnibase_spi.protocols.types.protocol_core_types import LiteralHealthStatus


@runtime_checkable
class ProtocolDirectKnowledgePipeline(Protocol):
    """
    Protocol for direct-to-database knowledge pipeline services.

    This protocol defines the standard interface that all direct knowledge
    pipeline implementations must follow, ensuring consistency across
    different storage backends and service implementations.
    """

    async def initialize(self) -> None:
        """
        Initialize the knowledge pipeline service and establish connections.

        Raises:
            Exception: If initialization fails
        """
        ...

    async def store_debug_log(
        self,
        debug_intelligence: "ProtocolAgentDebugIntelligence",
    ) -> str:
        """
        Store debug log directly to database bypassing repository.

        Args:
            debug_intelligence: Complete debug intelligence data model

        Returns:
            Log entry ID

        Raises:
            Exception: If storage fails
        """
        ...

    async def store_velocity_log(self, velocity_log: "ProtocolVelocityLog") -> str:
        """
        Store velocity tracking data directly to database.

        Args:
            velocity_log: Complete velocity log data model

        Returns:
            Velocity log ID

        Raises:
            Exception: If storage fails
        """
        ...

    async def store_pr_ticket(self, pr_ticket: "ProtocolPRTicket") -> str:
        """
        Store PR ticket with UUID tracking directly to database.

        Args:
            pr_ticket: Complete PR ticket data model

        Returns:
            PR ticket ID

        Raises:
            Exception: If storage fails
        """
        ...

    async def store_agent_action(self, agent_action: "ProtocolAgentAction") -> str:
        """
        Store agent action for audit trail and learning.

        Args:
            agent_action: Complete agent action data model

        Returns:
            Agent action ID

        Raises:
            Exception: If storage fails
        """
        ...

    async def get_velocity_analytics(
        self,
        agent_id: str | None = None,
        task_type: str | None = None,
        days: int | None = None,
    ) -> list["ProtocolAIExecutionMetrics"]:
        """
        Get velocity analytics for agents and tasks.

        Args:
            agent_id: Optional filter by specific agent
            task_type: Optional filter by task type
            days: Number of days to include in analysis

        Returns:
            List of velocity metrics

        Raises:
            Exception: If retrieval fails
        """
        ...

    async def get_agent_productivity(
        self,
        agent_id: str,
        days: int | None = None,
    ) -> list["ProtocolAIExecutionMetrics"]:
        """
        Get productivity metrics for a specific agent.

        Args:
            agent_id: ID of the agent to analyze
            days: Number of days to include in analysis

        Returns:
            List of productivity metrics

        Raises:
            Exception: If retrieval fails
        """
        ...

    async def search_debug_logs(
        self,
        agent_id: str | None = None,
        success: bool | None = None,
        keywords: str | None = None,
        limit: int | None = None,
    ) -> list["ProtocolAgentDebugIntelligence"]:
        """
        Search debug logs with filters.

        Args:
            agent_id: Optional filter by agent ID
            success: Optional filter by success status
            keywords: Optional keyword search in task descriptions
            limit: Maximum number of results to return

        Returns:
            List of debug intelligence entries

        Raises:
            Exception: If search fails
        """
        ...

    async def get_pr_tickets(
        self,
        agent_id: str | None = None,
        status: str | None = None,
        branch: str | None = None,
        limit: int | None = None,
    ) -> list["ProtocolPRTicket"]:
        """
        Get PR tickets with optional filters.

        Args:
            agent_id: Optional filter by agent ID
            status: Optional filter by PR status
            branch: Optional filter by branch name
            limit: Maximum number of results to return

        Returns:
            List of PR ticket entries

        Raises:
            Exception: If retrieval fails
        """
        ...

    async def get_agent_actions(
        self,
        agent_id: str | None = None,
        action_type: str | None = None,
        correlation_id: str | None = None,
        work_session_id: str | None = None,
        limit: int | None = None,
    ) -> list["ProtocolAgentAction"]:
        """
        Get agent actions with optional filters.

        Args:
            agent_id: Optional filter by agent ID
            action_type: Optional filter by action type
            correlation_id: Optional filter by correlation ID
            work_session_id: Optional filter by work session
            limit: Maximum number of results to return

        Returns:
            List of agent action entries

        Raises:
            Exception: If retrieval fails
        """
        ...

    async def emit_omnimemory_event(self, event: "ProtocolAgentAction") -> None:
        """
        Emit event to OmniMemory for learning and pattern recognition.

        Args:
            event: Agent action event to emit

        Raises:
            Exception: If event emission fails
        """
        ...

    async def health_check(self) -> "LiteralHealthStatus":
        """
        Check health of the knowledge pipeline service.

        Returns:
            Health status with metrics

        Raises:
            Exception: If health check fails
        """
        ...

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """
        Gracefully shutdown the knowledge pipeline service.

        Closes all database connections and releases any held resources.

        Args:
            timeout_seconds: Maximum time to wait for shutdown to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If shutdown does not complete within the specified timeout.
            Exception: If shutdown fails for other reasons.
        """
        ...

    @property
    async def is_connected(self) -> bool: ...
    @property
    def pipeline_type(self) -> str:
        """
        Get the type of knowledge pipeline implementation.

        Returns:
            Pipeline type identifier (e.g., 'postgresql', 'hybrid')
        """
        ...
