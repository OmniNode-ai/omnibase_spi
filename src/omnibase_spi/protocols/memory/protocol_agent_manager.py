"""
Protocol for Claude Code Agent Manager Service.

This protocol defines the interface for managing Claude Code agent instances,
including spawning, monitoring, lifecycle management, and resource tracking.
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Forward references for agent configuration and model types
    class ModelAgentConfig:
        """Protocol for agent configuration."""

        agent_id: str
        agent_type: str
        configuration: dict[str, Any]
        security_context: dict[str, Any]

    class ModelAgentInstance:
        """Protocol for agent instance."""

        instance_id: str
        agent_id: str
        status: str
        health_status: str
        configuration: "ModelAgentConfig"

    class ModelAgentHealthStatus:
        """Protocol for agent health status."""

        status: str
        last_check: str
        metrics: dict[str, Any]

    class ModelAgentStatus:
        """Protocol for agent status."""

        state: str
        error_message: str | None
        last_activity: str


@runtime_checkable
class ProtocolAgentManager(Protocol):
    """Protocol for managing Claude Code agent instances."""

    async def spawn_agent(self, config: "ModelAgentConfig") -> "ModelAgentInstance":
        """
        Spawn a new Claude Code agent instance.

        Args:
            config: Agent configuration including permissions and environment

        Returns:
            Agent instance with unique ID and status

        Raises:
            AgentSpawnError: If agent spawning fails
            ConfigurationError: If configuration is invalid
        """
        ...

    async def terminate_agent(self, agent_id: str) -> bool:
        """
        Terminate a Claude Code agent instance.

        Args:
            agent_id: Unique identifier of the agent to terminate

        Returns:
            True if termination was successful

        Raises:
            AgentNotFoundError: If agent ID doesn't exist
            TerminationError: If termination fails
        """
        ...

    async def get_agent(self, agent_id: str) -> "ModelAgentInstance" | None:
        """
        Retrieve agent instance by ID.

        Args:
            agent_id: Unique identifier of the agent

        Returns:
            Agent instance or None if not found
        """
        ...

    async def list_active_agents(self) -> list["ModelAgentInstance"]:
        """
        List all active agent instances.

        Returns:
            List of active agent instances
        """
        ...

    async def get_agent_status(self, agent_id: str) -> "ModelAgentStatus":
        """
        Get current status of an agent.

        Args:
            agent_id: Unique identifier of the agent

        Returns:
            Current agent status including health and activity

        Raises:
            AgentNotFoundError: If agent ID doesn't exist
        """
        ...

    async def health_check(self) -> "ModelAgentHealthStatus":
        """
        Perform health check on the agent manager service.

        Returns:
            Health status including system metrics
        """
        ...

    async def restart_agent(self, agent_id: str) -> "ModelAgentInstance":
        """
        Restart an existing agent instance.

        Args:
            agent_id: Unique identifier of the agent to restart

        Returns:
            Restarted agent instance

        Raises:
            AgentNotFoundError: If agent ID doesn't exist
            RestartError: If restart fails
        """
        ...

    async def update_agent_config(
        self,
        agent_id: str,
        config: "ModelAgentConfig",
    ) -> "ModelAgentInstance":
        """
        Update configuration of an existing agent.

        Args:
            agent_id: Unique identifier of the agent
            config: New configuration to apply

        Returns:
            Updated agent instance

        Raises:
            AgentNotFoundError: If agent ID doesn't exist
            ConfigurationError: If configuration is invalid
        """
        ...

    async def get_resource_usage(self, agent_id: str) -> dict[str, Any]:
        """
        Get resource usage metrics for an agent.

        Args:
            agent_id: Unique identifier of the agent

        Returns:
            Dictionary of resource usage metrics (CPU, memory, etc.)

        Raises:
            AgentNotFoundError: If agent ID doesn't exist
        """
        ...

    async def set_agent_idle(self, agent_id: str) -> bool:
        """
        Mark an agent as idle and available for work.

        Args:
            agent_id: Unique identifier of the agent

        Returns:
            True if agent was successfully marked idle

        Raises:
            AgentNotFoundError: If agent ID doesn't exist
        """
        ...

    async def set_agent_busy(self, agent_id: str, task_id: str) -> bool:
        """
        Mark an agent as busy with a specific task.

        Args:
            agent_id: Unique identifier of the agent
            task_id: Identifier of the task being executed

        Returns:
            True if agent was successfully marked busy

        Raises:
            AgentNotFoundError: If agent ID doesn't exist
        """
        ...
