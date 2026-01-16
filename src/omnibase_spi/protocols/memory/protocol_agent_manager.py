"""
Protocol for Claude Code Agent Manager Service.

This protocol defines the interface for managing Claude Code agent instances,
including spawning, monitoring, lifecycle management, and resource tracking.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType

from omnibase_spi.protocols.memory.protocol_agent_config_interfaces import (
    ProtocolAgentConfig,
)


@runtime_checkable
class ProtocolMemoryAgentInstance(Protocol):
    """
    Protocol for runtime agent instance representation.

    Represents a running AI agent instance with its runtime state,
    health information, and configuration. Provides read-only access
    to instance metadata for monitoring and management operations.

    Example:
        ```python
        async def monitor_agent(instance: ProtocolMemoryAgentInstance) -> dict:
            # Access instance metadata
            print(f"Instance: {instance.instance_id}")
            print(f"Agent: {instance.agent_id}")
            print(f"Status: {instance.status}")
            print(f"Health: {instance.health_status}")

            # Access configuration
            config = instance.configuration
            print(f"Model: {config.model}")
            print(f"Capabilities: {config.capabilities}")

            return {
                "instance_id": instance.instance_id,
                "status": instance.status,
                "health": instance.health_status,
            }
        ```

    Key Features:
        - **Unique Identification**: Instance and agent ID tracking
        - **Runtime Status**: Current execution state monitoring
        - **Health Monitoring**: Health status visibility
        - **Configuration Access**: Read-only configuration reference
        - **Immutable State**: Read-only properties for thread safety

    See Also:
        - ProtocolAgentConfig: Agent configuration structure
        - ProtocolAgentManager: Agent lifecycle management
        - ProtocolAgentStatus: Detailed status information
        - ProtocolAgentHealthStatus: Health check results
    """

    @property
    def instance_id(self) -> str:
        """Unique instance identifier."""
        ...

    @property
    def agent_id(self) -> str:
        """Agent identifier."""
        ...

    @property
    def status(self) -> str:
        """Current agent status."""
        ...

    @property
    def health_status(self) -> str:
        """Current health status."""
        ...

    @property
    def configuration(self) -> ProtocolAgentConfig:
        """Agent configuration."""
        ...


@runtime_checkable
class ProtocolAgentHealthStatus(Protocol):
    """
    Protocol for agent health status with metrics and check timestamps.

    Provides health information for an agent or agent manager service,
    including current health status, the timestamp of the last health
    check, and detailed metrics for monitoring and alerting systems.

    Attributes:
        status: Health status indicator ("healthy", "degraded", "unhealthy").
        last_check: ISO 8601 timestamp of the most recent health check.
        metrics: Dictionary of health metrics (CPU, memory, response time, etc.).

    Example:
        ```python
        class AgentHealthResult:
            @property
            def status(self) -> str:
                return "healthy"

            @property
            def last_check(self) -> str:
                return "2024-01-15T10:30:00Z"

            @property
            def metrics(self) -> dict[str, object]:
                return {
                    "cpu_percent": 25.5,
                    "memory_mb": 512,
                    "active_connections": 10,
                    "response_time_ms": 45
                }

        health = AgentHealthResult()
        assert isinstance(health, ProtocolAgentHealthStatus)
        assert health.status == "healthy"
        ```
    """

    @property
    def status(self) -> str:
        """Health status indicator."""
        ...

    @property
    def last_check(self) -> str:
        """Timestamp of last health check."""
        ...

    @property
    def metrics(self) -> "JsonType":
        """Health metrics data."""
        ...


@runtime_checkable
class ProtocolAgentStatus(Protocol):
    """
    Protocol for agent operational status with state and error tracking.

    Provides detailed status information for an individual agent instance,
    including current operational state, error details if applicable,
    and activity timestamps for monitoring agent lifecycle.

    Attributes:
        state: Current operational state ("idle", "busy", "starting", "stopping", "error").
        error_message: Detailed error message if state is "error"; None otherwise.
        last_activity: ISO 8601 timestamp of the agent's most recent activity.

    Example:
        ```python
        class BusyAgentStatus:
            @property
            def state(self) -> str:
                return "busy"

            @property
            def error_message(self) -> str | None:
                return None

            @property
            def last_activity(self) -> str:
                return "2024-01-15T10:35:00Z"

        class ErrorAgentStatus:
            @property
            def state(self) -> str:
                return "error"

            @property
            def error_message(self) -> str | None:
                return "Connection timeout after 30s"

            @property
            def last_activity(self) -> str:
                return "2024-01-15T10:30:00Z"

        status = BusyAgentStatus()
        assert isinstance(status, ProtocolAgentStatus)
        assert status.error_message is None
        ```
    """

    @property
    def state(self) -> str:
        """Current agent state."""
        ...

    @property
    def error_message(self) -> str | None:
        """Error message if in error state."""
        ...

    @property
    def last_activity(self) -> str:
        """Timestamp of last activity."""
        ...


@runtime_checkable
class ProtocolAgentManager(Protocol):
    """Protocol for managing Claude Code agent instances."""

    async def spawn_agent(
        self, config: ProtocolAgentConfig
    ) -> ProtocolMemoryAgentInstance:
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

    async def get_agent(self, agent_id: str) -> ProtocolMemoryAgentInstance | None:
        """
        Retrieve agent instance by ID.

        Args:
            agent_id: Unique identifier of the agent

        Returns:
            Agent instance or None if not found
        """
        ...

    async def list_active_agents(self) -> list[ProtocolMemoryAgentInstance]:
        """
        List all active agent instances.

        Returns:
            List of active agent instances
        """
        ...

    async def get_agent_status(self, agent_id: str) -> ProtocolAgentStatus:
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

    async def health_check(self) -> ProtocolAgentHealthStatus:
        """
        Perform health check on the agent manager service.

        Returns:
            Health status including system metrics
        """
        ...

    async def restart_agent(self, agent_id: str) -> ProtocolMemoryAgentInstance:
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
        config: ProtocolAgentConfig,
    ) -> ProtocolMemoryAgentInstance:
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

    async def get_resource_usage(self, agent_id: str) -> "JsonType":
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
