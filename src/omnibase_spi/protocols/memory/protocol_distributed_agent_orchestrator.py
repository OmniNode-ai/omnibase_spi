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

    class ModelValidationResult:
        """Protocol for validation results."""

        is_valid: bool
        errors: list[str]
        warnings: list[str]

    class ModelMemoryOperation:
        """Protocol for memory operations."""

        operation_type: str
        data: dict[str, Any]
        timestamp: str

    class ModelMemoryResponse:
        """Protocol for memory responses."""

        success: bool
        data: Any
        error_message: str | None

    class ModelMemoryMetadata:
        """Protocol for memory metadata."""

        size: int
        created_at: str
        modified_at: str
        access_count: int

    class ModelMemoryError:
        """Protocol for memory errors."""

        error_type: str
        message: str
        details: dict[str, Any]

    class ModelMemoryRequest:
        """Protocol for memory requests."""

        operation: str
        key: str
        data: Any
        options: dict[str, Any]

    class ModelMemoryResponseV2:
        """Protocol for memory responses (version 2)."""

        success: bool
        data: Any
        error: str | None

    class ModelMemorySecurityContext:
        """Protocol for memory security context."""

        user_id: str
        permissions: list[str]
        session_id: str

    class ModelMemoryStreamingResponse:
        """Protocol for streaming memory responses."""

        chunk_id: str
        data: Any
        is_last: bool

    class ModelMemoryStreamingRequest:
        """Protocol for streaming memory requests."""

        stream_id: str
        operation: str
        parameters: dict[str, Any]

    class ModelMemorySecurityPolicy:
        """Protocol for memory security policies."""

        policy_id: str
        rules: list[dict[str, Any]]
        default_action: str

    class ModelMemoryComposable:
        """Protocol for composable memory operations."""

        components: list[str]
        operations: list[str]
        metadata: dict[str, Any]

    class ModelMemoryErrorHandling:
        """Protocol for memory error handling."""

        error_type: str
        severity: str
        recovery_strategy: str
        context: dict[str, Any]


"""
Protocol for Distributed Agent Orchestrator.

Defines the interface for orchestrating agents across multiple devices
with location-aware routing, failover, and load balancing capabilities.
"""


if TYPE_CHECKING:
    from typing import Literal

    EnumAgentCapability = Literal["capability_placeholder"]


@runtime_checkable
class ProtocolDistributedAgentOrchestrator(Protocol):
    """Protocol for distributed agent orchestration across multiple devices."""

    async def spawn_agents_for_device(
        self,
        device_name: str,
    ) -> list["ModelAgentInstance"]:
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
        prefer_local: bool = True,
        required_capabilities: list[EnumAgentCapability] | None = None,
    ) -> Any:
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
        required_capabilities: list[EnumAgentCapability] | None = None,
        prefer_local: bool = True,
    ) -> "ModelAgentInstance" | None:
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

    async def get_agent_summary(self) -> dict[str, Any]:
        """
        Get summary of all agents and their status.

        Returns:
            Comprehensive agent summary with health and status information
        """
        ...

    async def health_check_agents(self) -> dict[str, "ModelAgentHealthStatus"]:
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

    def set_location(self, location: str) -> None: ...
    async def get_device_agents(self, device_name: str) -> list["ModelAgentInstance"]:
        """
        Get all agents running on a specific device.

        Args:
            device_name: Name of the device

        Returns:
            List of agent instances on the device
        """
        ...

    async def get_agents_by_role(self, role: str) -> list["ModelAgentInstance"]:
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

    async def restart_agent(self, agent_id: str) -> "ModelAgentInstance":
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
