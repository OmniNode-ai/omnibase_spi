"""
Protocol for LLM Agent Provider.

Defines the interface for providing LLM-based agents using various providers
with unified agent management and task routing.
"""

from typing import Literal, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue

# Type definitions for LLM Agent Provider
LiteralAgentCapability = Literal[
    "code_generation",
    "data_analysis",
    "document_processing",
    "natural_language_processing",
    "reasoning",
    "planning",
    "validation",
    "testing",
    "monitoring",
    "coordination",
]

LiteralLLMProvider = Literal[
    "openai",
    "anthropic",
    "cohere",
    "huggingface",
    "local",
    "custom",
    "bedrock",
    "vertexai",
    "azure",
]


@runtime_checkable
class ProtocolLLMAgentConfig(Protocol):
    """
    Protocol for LLM agent configuration.

    Defines the interface for LLM agent configuration including provider settings,
    model parameters, capabilities, and metadata for multi-provider LLM integration.

    Example:
        @runtime_checkable
        class OpenAIAgentConfig(Protocol):
            @property
            def provider(self) -> LiteralLLMProvider: ...
            @property
            def model_name(self) -> str: ...
            @property
            def api_key(self) -> str | None: ...
            @property
            def max_tokens(self) -> int: ...
            @property
            def temperature(self) -> float: ...
            @property
            def timeout_seconds(self) -> int: ...
            @property
            def system_prompt(self) -> str | None: ...
            @property
            def capabilities(self) -> list[LiteralAgentCapability]: ...
            @property
            def metadata(self) -> dict[str, ContextValue]: ...

            async def validate_config(self) -> bool: ...
    """

    provider: LiteralLLMProvider
    model_name: str
    api_key: str | None
    base_url: str | None
    max_tokens: int
    temperature: float
    timeout_seconds: int
    system_prompt: str | None
    capabilities: list[LiteralAgentCapability]
    metadata: dict[str, ContextValue]


@runtime_checkable
class ProtocolMcpAgentInstance(Protocol):
    """
    Protocol for agent instance.

    Defines the interface for LLM agent instances with runtime state tracking,
    capability management, and lifecycle monitoring for distributed agent coordination.

    Example:
        @runtime_checkable
        class AgentInstance(Protocol):
            @property
            def agent_id(self) -> str: ...
            @property
            def provider(self) -> LiteralLLMProvider: ...
            @property
            def model_name(self) -> str: ...
            @property
            def status(self) -> str: ...
            @property
            def capabilities(self) -> list[LiteralAgentCapability]: ...
            @property
            def created_at(self) -> str: ...
            @property
            def last_activity(self) -> str: ...
            @property
            def metadata(self) -> dict[str, ContextValue]: ...

            async def update_status(self, new_status: str) -> None: ...
            async def add_capability(self, capability: LiteralAgentCapability) -> bool: ...
    """

    agent_id: str
    provider: LiteralLLMProvider
    model_name: str
    status: str
    capabilities: list[LiteralAgentCapability]
    created_at: str
    last_activity: str
    metadata: dict[str, ContextValue]


@runtime_checkable
class ProtocolLLMAgentResponse(Protocol):
    """
    Protocol for LLM response.

    Defines the interface for standardized LLM responses with usage tracking,
    metadata management, and performance monitoring for multi-provider integration.

    Example:
        @runtime_checkable
        class LLMResponse(Protocol):
            @property
            def content(self) -> str: ...
            @property
            def role(self) -> str: ...
            @property
            def finish_reason(self) -> str: ...
            @property
            def usage(self) -> dict[str, int]: ...
            @property
            def model(self) -> str: ...
            @property
            def timestamp(self) -> str: ...
            @property
            def metadata(self) -> dict[str, ContextValue]: ...

            def calculate_cost(self) -> float: ...
            def is_successful(self) -> bool: ...
    """

    content: str
    role: str
    finish_reason: str
    usage: dict[str, int]
    model: str
    timestamp: str
    metadata: dict[str, ContextValue]


@runtime_checkable
class ProtocolLLMAgentProvider(Protocol):
    """
    Protocol for providing LLM-based agents using various providers.

    Defines the interface for unified LLM agent management across multiple providers
    with agent lifecycle management, capability-based routing, and health monitoring.

    Key Features:
        - **Multi-Provider Support**: Unified interface for OpenAI, Anthropic, local models, etc.
        - **Agent Lifecycle**: Complete agent management from spawning to termination
        - **Capability-Based Routing**: Route tasks to agents with specific capabilities
        - **Health Monitoring**: Track agent health and performance metrics
        - **Resource Management**: Optimize resource usage across multiple agent instances
        - **Provider Abstraction**: Switch between providers without changing client code

    Example:
        class MultiProviderLLMAgentProvider(ProtocolLLMAgentProvider):
            async def spawn_agent(self, config):
                # Spawn agent based on provider configuration
                if config.provider == "openai":
                    agent = OpenAIAgent(config)
                elif config.provider == "anthropic":
                    agent = AnthropicAgent(config)
                else:
                    agent = LocalLLMAgent(config)

                await agent.initialize()
                return AgentInstance(
                    agent_id=str(uuid.uuid4()),
                    provider=config.provider,
                    model_name=config.model_name,
                    status="active",
                    capabilities=config.capabilities,
                    created_at=datetime.utcnow().isoformat(),
                    last_activity=datetime.utcnow().isoformat(),
                    metadata={"config": config.metadata}
                )

            async def execute_task(self, agent_id, prompt, system_prompt=None):
                # Route task to appropriate agent
                agent = await self.get_agent(agent_id)
                if not agent:
                    raise ValueError(f"Agent {agent_id} not found")

                response = await agent.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt
                )

                return LLMResponse(
                    content=response.content,
                    role=response.role,
                    finish_reason=response.finish_reason,
                    usage=response.usage,
                    model=response.model,
                    timestamp=datetime.utcnow().isoformat(),
                    metadata={"agent_id": agent_id, "latency_ms": response.latency_ms}
                )
    """

    async def spawn_agent(
        self, config: ProtocolLLMAgentConfig
    ) -> ProtocolMcpAgentInstance:
        """
        Spawn a new LLM agent instance.

        Args:
            config: Agent configuration including provider and model settings

        Returns:
            Spawned agent instance
        """
        ...

    async def terminate_agent(self, agent_id: str) -> bool:
        """
        Terminate an existing agent.

        Args:
            agent_id: ID of the agent to terminate

        Returns:
            True if termination was successful
        """
        ...

    async def get_agent(self, agent_id: str) -> ProtocolMcpAgentInstance | None:
        """
        Get agent instance by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent instance or None if not found
        """
        ...

    async def list_active_agents(self) -> list[ProtocolMcpAgentInstance]:
        """
        List all active agent instances.

        Returns:
            List of active agent instances
        """
        ...

    async def execute_task(
        self,
        agent_id: str,
        prompt: str,
        system_prompt: str | None = None,
    ) -> ProtocolLLMAgentResponse:
        """
        Execute a task using a specific agent.

        Args:
            agent_id: ID of the agent to use
            prompt: Task prompt
            system_prompt: Optional system prompt

        Returns:
            Response from the agent
        """
        ...

    async def get_agents_by_capability(
        self,
        capability: LiteralAgentCapability,
    ) -> list[ProtocolMcpAgentInstance]:
        """
        Get agents that have a specific capability.

        Args:
            capability: Required capability

        Returns:
            List of agents with the specified capability
        """
        ...

    async def get_agents_by_provider(
        self,
        provider: LiteralLLMProvider,
    ) -> list[ProtocolMcpAgentInstance]:
        """
        Get agents using a specific LLM provider.

        Args:
            provider: LLM provider type

        Returns:
            List of agents using the specified provider
        """
        ...

    async def health_check_agents(self) -> dict[str, str]:
        """
        Perform health check on all agents.

        Returns:
            Dictionary mapping agent IDs to health status
        """
        ...

    async def get_provider_status(self, provider: LiteralLLMProvider) -> str:
        """
        Get status of a specific LLM provider.

        Args:
            provider: Provider to check

        Returns:
            Provider status (available, unavailable, degraded)
        """
        ...

    async def restart_agent(self, agent_id: str) -> ProtocolMcpAgentInstance:
        """
        Restart an existing agent.

        Args:
            agent_id: ID of the agent to restart

        Returns:
            Restarted agent instance
        """
        ...
