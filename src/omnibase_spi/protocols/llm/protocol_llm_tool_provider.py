"""
Protocol for LLM tool provider.

Defines the interface for providing LLM tools including model router and providers
without direct imports, enabling proper dependency injection and registry patterns.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Forward reference for LLM provider to maintain namespace isolation
    @runtime_checkable
    class ProtocolLLMProviderImpl(Protocol):
        """
        Protocol for LLM provider implementation interface.

        Defines the interface for concrete LLM provider implementations
        (Ollama, OpenAI, Anthropic, Gemini) used within the tool provider
        system. This is a forward-declared protocol for type checking only.

        Example:
            ```python
            async def use_provider(provider: ProtocolLLMProviderImpl) -> dict:
                # Provider implementation provides model-specific operations
                models = await provider.get_available_models()
                response = await provider.generate(request)
                return {"models": models, "response": response}
            ```

        Key Features:
            - **Type-Safe Forward Reference**: Enables TYPE_CHECKING imports
            - **Provider Abstraction**: Supports multiple LLM provider backends
            - **Namespace Isolation**: Prevents circular import dependencies
            - **Registry Integration**: Compatible with provider registry systems

        See Also:
            - ProtocolLLMProvider: Main provider protocol interface
            - ProtocolModelRouter: Multi-provider routing protocol
            - ProtocolLLMToolProvider: Tool provider composition protocol
        """

        ...


@runtime_checkable
class ProtocolModelRouter(Protocol):
    """
    Protocol for intelligent multi-provider LLM routing.

    Coordinates request routing across multiple LLM providers based on
    capabilities, cost, performance, and availability. Implements provider
    selection, load balancing, and failover strategies.

    Example:
        ```python
        async def route_request(
            router: ProtocolModelRouter, request: object
        ) -> object:
            # Router intelligently selects best provider
            response = await router.generate(request)

            # Check available backends
            providers = await router.get_available_providers()
            print(f"Available: {providers}")

            return response
        ```

    Key Features:
        - **Intelligent Routing**: Selects optimal provider per request
        - **Multi-Provider**: Coordinates Ollama, OpenAI, Anthropic, Gemini
        - **Load Balancing**: Distributes requests across providers
        - **Failover Support**: Automatic fallback on provider failure
        - **Cost Optimization**: Routes based on cost/performance tradeoffs

    See Also:
        - ProtocolLLMProvider: Individual provider protocol
        - ProtocolLLMToolProvider: Tool provider composition
        - ProtocolLLMRequest: Request structure for routing
    """

    async def generate(self, request: object) -> object:
        """Generate response using the model router."""
        ...

    async def get_available_providers(self) -> list[str]:
        """Get list of available providers."""
        ...


@runtime_checkable
class ProtocolLLMToolProvider(Protocol):
    """Protocol for unified LLM tool provisioning and routing coordination.

    Provides centralized access to LLM providers (Ollama, OpenAI, Anthropic,
    Gemini) and intelligent routing capabilities for multi-provider workflow
    orchestration without direct implementation dependencies.

    Example:
        ```python
        async def use_llm_tools(
            tool_provider: ProtocolLLMToolProvider,
            prompt: str
        ) -> str:
            # Get intelligent router for automatic provider selection
            router = await tool_provider.get_model_router()
            request = create_llm_request(prompt=prompt)
            response = await router.generate(request)

            # Or access specific provider directly
            ollama = await tool_provider.get_ollama_provider()
            local_response = await ollama.generate_async(request)

            return response.content
        ```

    Key Features:
        - **Multi-Provider Access**: Unified interface to all LLM providers
        - **Intelligent Routing**: Automatic provider selection via router
        - **Dependency Injection**: Registry-based provider resolution
        - **Provider Isolation**: Clean boundaries between provider implementations
        - **Configuration Management**: Centralized provider configuration
        - **Failover Support**: Automatic fallback across providers

    See Also:
        - ProtocolModelRouter: Intelligent multi-provider routing protocol
        - ProtocolLLMProvider: Individual provider protocol interface
        - ProtocolLLMRequest: Request structure for provider operations
        - ProtocolProviderConfig: Provider configuration protocol
    """

    async def get_model_router(self) -> "ProtocolModelRouter":
        """Get configured model router with registered providers.

        Returns:
            Model router configured with all available providers

        Raises:
            RuntimeError: If router initialization fails
            ConfigurationError: If provider configuration is invalid

        Example:
            ```python
            router = await tool_provider.get_model_router()
            providers = await router.get_available_providers()
            print(f"Router has {len(providers)} providers")

            # Router automatically selects best provider
            response = await router.generate(request)
            ```
        """
        ...

    async def get_gemini_provider(self) -> "ProtocolLLMProviderImpl":
        """Get Gemini LLM provider instance.

        Returns:
            Configured Gemini provider with Google AI integration

        Raises:
            ProviderNotAvailableError: If Gemini provider is not configured
            AuthenticationError: If API key is invalid

        Example:
            ```python
            gemini = await tool_provider.get_gemini_provider()
            models = await gemini.get_available_models()
            # Use Gemini-specific features like function calling
            response = await gemini.generate_async(request)
            ```
        """
        ...

    async def get_openai_provider(self) -> "ProtocolLLMProviderImpl":
        """Get OpenAI LLM provider instance.

        Returns:
            Configured OpenAI provider with GPT model access

        Raises:
            ProviderNotAvailableError: If OpenAI provider is not configured
            AuthenticationError: If API key is invalid

        Example:
            ```python
            openai = await tool_provider.get_openai_provider()
            caps = await openai.get_model_capabilities("gpt-4")
            if caps.context_length >= 128000:
                # Use for long-context tasks
                response = await openai.generate_async(request)
            ```
        """
        ...

    async def get_ollama_provider(self) -> "ProtocolLLMProviderImpl":
        """Get Ollama LLM provider instance for local models.

        Returns:
            Configured Ollama provider with local model access

        Raises:
            ProviderNotAvailableError: If Ollama service is not running
            ConnectionError: If cannot connect to Ollama service

        Example:
            ```python
            ollama = await tool_provider.get_ollama_provider()
            # Local models have zero API cost
            cost = ollama.estimate_cost(request)  # Returns 0.0
            response = await ollama.generate_async(request)
            ```
        """
        ...

    async def get_claude_provider(self) -> "ProtocolLLMProviderImpl":
        """Get Claude LLM provider instance (Anthropic).

        Returns:
            Configured Claude provider with Anthropic API access

        Raises:
            ProviderNotAvailableError: If Claude provider is not configured
            AuthenticationError: If API key is invalid

        Example:
            ```python
            claude = await tool_provider.get_claude_provider()
            # Use Claude for analysis tasks
            request = create_llm_request(
                model="claude-3-opus",
                prompt="Analyze this code",
                temperature=0.3
            )
            response = await claude.generate_async(request)
            ```
        """
        ...
