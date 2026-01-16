"""Protocol for universal LLM provider operations with model-agnostic interface."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Iterator
from typing import (
    TYPE_CHECKING,
    Protocol,
    runtime_checkable,
)

if TYPE_CHECKING:
    from omnibase_core.types import JsonType
    from omnibase_spi.protocols.types.protocol_llm_types import (
        ProtocolLLMHealthResponse,
        ProtocolLLMRequest,
        ProtocolLLMResponse,
        ProtocolModelCapabilities,
        ProtocolProviderConfig,
    )


@runtime_checkable
class ProtocolLLMProvider(Protocol):
    """Universal protocol for model-agnostic LLM provider operations.

    Defines the standard interface that all LLM providers (Ollama, OpenAI,
    Anthropic, Gemini) must implement for seamless provider switching,
    intelligent routing, and unified workflow integration across local
    and external model services.

    Example:
        ```python
        async def use_llm_provider(
            provider: ProtocolLLMProvider,
            prompt: str
        ) -> str:
            # Check provider availability
            if not provider.is_available:
                raise RuntimeError(f"{provider.provider_name} unavailable")

            # Configure provider
            config = create_provider_config(
                api_key="key", base_url="http://localhost:11434"
            )
            provider.configure(config)

            # Get available models
            models = await provider.get_available_models()
            print(f"Available: {models}")

            # Create and execute request
            request = create_llm_request(
                model=models[0], prompt=prompt, temperature=0.7
            )
            response = await provider.generate_async(request)

            return response.content
        ```

    Key Features:
        - **Provider Abstraction**: Unified interface across all LLM providers
        - **Intelligent Routing**: Provider selection based on capabilities
        - **Cost Estimation**: Per-request cost calculation for budgeting
        - **Health Monitoring**: Real-time provider availability tracking
        - **Streaming Support**: Async streaming for real-time responses
        - **Capability Discovery**: Dynamic model capability querying
        - **Type Safety**: Strong typing with protocol-based contracts

    See Also:
        - ProtocolModelRouter: Multi-provider intelligent routing
        - ProtocolLLMToolProvider: Tool provider composition protocol
        - ProtocolLLMRequest: Request structure for provider operations
        - ProtocolLLMResponse: Response structure with usage metrics
    """

    @property
    def provider_name(self) -> str:
        """Get the provider name identifier.

        Returns:
            Provider name (e.g., 'ollama', 'openai', 'anthropic', 'gemini')

        Example:
            ```python
            provider = get_llm_provider()
            print(f"Using provider: {provider.provider_name}")
            ```
        """
        ...

    @property
    def provider_type(self) -> str:
        """Get the provider deployment type classification.

        Returns:
            Provider type: 'local', 'external_trusted', or 'external'

        Example:
            ```python
            if provider.provider_type == "local":
                print("Using local model - no API costs")
            else:
                print("Using external API - cost tracking enabled")
            ```
        """
        ...

    @property
    def is_available(self) -> bool:
        """Check if the provider is currently available and healthy.

        Returns:
            True if provider is operational, False otherwise

        Example:
            ```python
            if not provider.is_available:
                fallback_provider = get_fallback_provider()
                return await fallback_provider.generate_async(request)
            ```
        """
        ...

    def configure(self, config: ProtocolProviderConfig) -> None:
        """Configure the provider with connection and authentication details.

        Args:
            config: Provider configuration with API keys, URLs, timeouts

        Raises:
            ValueError: If configuration is invalid
            ConnectionError: If provider cannot be reached

        Example:
            ```python
            config = ProtocolProviderConfig(
                api_key="sk-...",
                base_url="https://api.openai.com/v1",
                timeout=30,
                max_retries=3
            )
            provider.configure(config)
            ```
        """
        ...

    async def get_available_models(self) -> list[str]:
        """Get list of available models from this provider.

        Returns:
            List of model identifiers available on this provider

        Raises:
            ConnectionError: If provider cannot be reached
            TimeoutError: If request exceeds timeout

        Example:
            ```python
            models = await provider.get_available_models()
            print(f"Provider offers {len(models)} models")
            for model in models:
                caps = await provider.get_model_capabilities(model)
                print(f"  {model}: {caps.context_length} tokens")
            ```
        """
        ...

    async def get_model_capabilities(
        self, model_name: str
    ) -> ProtocolModelCapabilities:
        """Get capabilities information for a specific model.

        Args:
            model_name: Model identifier to query

        Returns:
            Model capabilities with context length, features, pricing

        Raises:
            ValueError: If model_name is invalid
            KeyError: If model not found on provider

        Example:
            ```python
            caps = await provider.get_model_capabilities("gpt-4")
            if caps.supports_function_calling:
                print(f"Model has {caps.context_length} context")
                print(f"Cost: ${caps.cost_per_1k_tokens}/1k tokens")
            ```
        """
        ...

    def validate_request(self, request: ProtocolLLMRequest) -> bool:
        """Validate that the request is compatible with this provider.

        Args:
            request: LLM request to validate

        Returns:
            True if request is valid for this provider, False otherwise

        Example:
            ```python
            request = create_llm_request(
                model="claude-3-opus", prompt="Hello"
            )
            if not provider.validate_request(request):
                raise ValueError("Request incompatible with provider")
            ```
        """
        ...

    async def generate(self, request: ProtocolLLMRequest) -> ProtocolLLMResponse:
        """Generate a response using this provider (synchronous-style).

        Args:
            request: The LLM request with prompt and parameters

        Returns:
            ProtocolLLMResponse: Generated response with usage metrics

        Raises:
            ProviderError: If generation fails
            ValidationError: If request is invalid
            TimeoutError: If request exceeds timeout

        Example:
            ```python
            request = create_llm_request(
                model="gpt-4", prompt="Explain ONEX", temperature=0.7
            )
            response = await provider.generate(request)
            print(f"Response: {response.content}")
            print(f"Tokens: {response.usage.total_tokens}")
            ```
        """
        ...

    def generate_stream(self, request: ProtocolLLMRequest) -> Iterator[str]:
        """Generate a streaming response using this provider (synchronous).

        Args:
            request: The LLM request with prompt and parameters

        Yields:
            str: Streaming response chunks

        Raises:
            ProviderError: If generation fails
            ValidationError: If request is invalid

        Example:
            ```python
            request = create_llm_request(model="gpt-4", prompt="Write story")
            for chunk in provider.generate_stream(request):
                print(chunk, end="", flush=True)
            ```
        """
        ...

    async def generate_async(self, request: ProtocolLLMRequest) -> ProtocolLLMResponse:
        """Generate a response asynchronously using this provider.

        Args:
            request: The LLM request with prompt and parameters

        Returns:
            ProtocolLLMResponse: Generated response with usage metrics

        Raises:
            ProviderError: If generation fails
            ValidationError: If request is invalid
            TimeoutError: If request exceeds timeout

        Example:
            ```python
            # Parallel generation across multiple providers
            async def multi_provider_generate(request):
                providers = [openai, anthropic, gemini]
                tasks = [p.generate_async(request) for p in providers]
                responses = await asyncio.gather(*tasks)
                return select_best_response(responses)
            ```
        """
        ...

    def generate_stream_async(
        self,
        request: ProtocolLLMRequest,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response asynchronously using this provider.

        Args:
            request: The LLM request with prompt and parameters

        Yields:
            str: Streaming response chunks

        Raises:
            ProviderError: If generation fails
            ValidationError: If request is invalid

        Example:
            ```python
            request = create_llm_request(model="claude-3", prompt="Analyze")
            async for chunk in provider.generate_stream_async(request):
                await websocket.send(chunk)  # Real-time streaming
            ```
        """
        ...

    def estimate_cost(self, request: ProtocolLLMRequest) -> float:
        """Estimate the cost for this request with this provider.

        Args:
            request: The LLM request to estimate cost for

        Returns:
            float: Estimated cost in USD (0.0 for local providers)

        Example:
            ```python
            request = create_llm_request(model="gpt-4", prompt="Long analysis")
            cost = provider.estimate_cost(request)
            if cost > max_budget:
                # Route to cheaper provider
                request.model = "gpt-3.5-turbo"
            ```
        """
        ...

    async def health_check(self) -> ProtocolLLMHealthResponse:
        """Perform a health check on the provider.

        Returns:
            ProtocolLLMHealthResponse: Strongly-typed health status information

        Example:
            ```python
            health = await provider.health_check()
            if not health.is_healthy:
                logger.error(f"Provider unhealthy: {health.error_message}")
                return await fallback_provider.health_check()
            print(f"Latency: {health.latency_ms}ms")
            ```
        """
        ...

    async def get_provider_info(self) -> JsonType:
        """Get comprehensive provider information.

        Returns:
            Dictionary with provider metadata, configuration, and statistics

        Example:
            ```python
            info = await provider.get_provider_info()
            print(f"Provider: {info['name']}")
            print(f"Models: {len(info['available_models'])}")
            print(f"Uptime: {info['uptime_seconds']}s")
            ```
        """
        ...

    def supports_streaming(self) -> bool:
        """Check if provider supports streaming responses.

        Returns:
            True if streaming is supported, False otherwise

        Example:
            ```python
            if provider.supports_streaming():
                async for chunk in provider.generate_stream_async(request):
                    yield chunk
            else:
                response = await provider.generate_async(request)
                yield response.content
            ```
        """
        ...

    def supports_async(self) -> bool:
        """Check if provider supports async operations.

        Returns:
            True if async operations supported, False otherwise

        Example:
            ```python
            if provider.supports_async():
                response = await provider.generate_async(request)
            else:
                response = await asyncio.to_thread(
                    provider.generate, request
                )
            ```
        """
        ...
