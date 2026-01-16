"""
Protocol for Distributed Agent Orchestrator.

Defines the interface for orchestrating agents across multiple devices
with location-aware routing, failover, and load balancing capabilities.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.memory.protocol_agent_manager import (
    ProtocolAgentHealthStatus,
    ProtocolMemoryAgentInstance,
)

# Protocol definitions for type checking
if TYPE_CHECKING:
    from typing import Literal

    from omnibase_core.types import JsonType

    EnumAgentCapability = Literal["capability_placeholder"]


@runtime_checkable
class ProtocolDistributedAgentOrchestrator(Protocol):
    """Protocol for distributed agent orchestration across multiple devices."""

    async def spawn_agents_for_device(
        self,
        device_name: str,
    ) -> list[ProtocolMemoryAgentInstance]:
        """
        Spawn agents for a specific device based on configuration.

        Args:
            device_name: Name of the device to spawn agents for

        Returns:
            List of spawned agent instances

        Raises:
            DeviceNotFoundError: If device configuration doesn't exist
            AgentSpawnError: If agent spawning fails
        """
        ...

    async def route_task(
        self,
        task_type: str,
        prompt: str,
        system_prompt: str | None = None,
        prefer_local: bool | None = None,
        required_capabilities: list["EnumAgentCapability"] | None = None,
    ) -> object:
        """
        Route a task to the most appropriate agent.

        Args:
            task_type: Type of task to route
            prompt: Task prompt
            system_prompt: Optional system prompt
            prefer_local: Whether to prefer local agents over remote
            required_capabilities: Required agent capabilities

        Returns:
            Response from the selected agent

        Raises:
            NoAgentsAvailableError: If no suitable agents are available
            TaskRoutingError: If task routing fails
        """
        ...

    async def find_best_agent(
        self,
        task_type: str,
        required_capabilities: list["EnumAgentCapability"] | None = None,
        prefer_local: bool | None = None,
    ) -> ProtocolMemoryAgentInstance | None:
        """
        Find the best agent for a given task type.

        Args:
            task_type: Type of task
            required_capabilities: Required capabilities
            prefer_local: Whether to prefer local agents

        Returns:
            Best agent instance or None if no suitable agent found
        """
        ...

    async def get_agent_summary(self) -> "JsonType":
        """
        Get summary of all agents and their status.

        Returns:
            Comprehensive agent summary with health and status information
        """
        ...

    async def health_check_agents(self) -> dict[str, ProtocolAgentHealthStatus]:
        """
        Perform health check on all active agents.

        Returns:
            Dictionary mapping agent IDs to health status
        """
        ...

    async def rebalance_agents(self) -> bool:
        """
        Rebalance agents across devices based on current load.

        Returns:
            True if rebalancing was successful

        Raises:
            RebalancingError: If rebalancing fails
        """
        ...

    def set_location(self, location: str) -> None:
        """
        Set the current location for routing decisions.

        Args:
            location: Location identifier
        """
        ...

    async def get_device_agents(
        self, device_name: str
    ) -> list[ProtocolMemoryAgentInstance]:
        """
        Get all agents running on a specific device.

        Args:
            device_name: Name of the device

        Returns:
            List of agent instances on the device
        """
        ...

    async def get_agents_by_role(self, role: str) -> list[ProtocolMemoryAgentInstance]:
        """
        Get all agents with a specific role.

        Args:
            role: Agent role to search for

        Returns:
            List of agent instances with the specified role
        """
        ...

    async def terminate_agent(self, agent_id: str) -> bool:
        """
        Terminate a specific agent.

        Args:
            agent_id: ID of the agent to terminate

        Returns:
            True if termination was successful

        Raises:
            AgentNotFoundError: If agent doesn't exist
        """
        ...

    async def restart_agent(self, agent_id: str) -> ProtocolMemoryAgentInstance:
        """
        Restart a specific agent.

        Args:
            agent_id: ID of the agent to restart

        Returns:
            Restarted agent instance

        Raises:
            AgentNotFoundError: If agent doesn't exist
            RestartError: If restart fails
        """
        ...
