from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Iterator,
    Protocol,
    runtime_checkable,
)

"""
Universal LLM provider protocol for model-agnostic operations.

Defines the standard interface that all LLM providers must implement
for seamless provider switching and intelligent routing.
"""

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_llm_types import (
        ProtocolLLMHealthResponse,
        ProtocolLLMRequest,
        ProtocolLLMResponse,
        ProtocolModelCapabilities,
        ProtocolProviderConfig,
    )


@runtime_checkable
class ProtocolLLMProvider(Protocol):
    """
    Universal protocol for LLM providers.

    Defines the standard interface that all LLM providers
    (Ollama, OpenAI, Anthropic) must implement for seamless
    integration and intelligent routing capabilities.
    """

    @property
    def provider_name(self) -> str:
        """Get the provider name (e.g., 'ollama', 'openai', 'anthropic')."""
        ...

    @property
    def provider_type(self) -> str:
        """Get the provider type ('local', 'external_trusted', 'external')."""
        ...

    @property
    def is_available(self) -> bool:
        """Check if the provider is currently available and healthy."""
        ...

    def configure(self, config: "ProtocolProviderConfig") -> None:
        """Configure the provider with connection and authentication details."""
        ...

    async def get_available_models(self) -> list[str]:
        """Get list[Any]of available models from this provider."""
        ...

    async def get_model_capabilities(
        self, model_name: str
    ) -> "ProtocolModelCapabilities":
        """Get capabilities information for a specific model."""
        ...

    def validate_request(self, request: "ProtocolLLMRequest") -> bool:
        """Validate that the request is compatible with this provider."""
        ...

    async def generate(self, request: "ProtocolLLMRequest") -> "ProtocolLLMResponse":
        """
        Generate a response using this provider.

        Args:
            request: The LLM request with prompt and parameters

        Returns:
            ProtocolLLMResponse: Generated response with usage metrics

        Raises:
            ProviderError: If generation fails
            ValidationError: If request is invalid
        """
        ...

    def generate_stream(self, request: "ProtocolLLMRequest") -> Iterator[str]:
        """
        Generate a streaming response using this provider.

        Args:
            request: The LLM request with prompt and parameters

        Yields:
            str: Streaming response chunks

        Raises:
            ProviderError: If generation fails
            ValidationError: If request is invalid
        """
        ...

    async def generate_async(
        self, request: "ProtocolLLMRequest"
    ) -> "ProtocolLLMResponse":
        """
        Generate a response asynchronously using this provider.

        Args:
            request: The LLM request with prompt and parameters

        Returns:
            ProtocolLLMResponse: Generated response with usage metrics

        Raises:
            ProviderError: If generation fails
            ValidationError: If request is invalid
        """
        ...

    def generate_stream_async(
        self,
        request: "ProtocolLLMRequest",
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response asynchronously using this provider.

        Args:
            request: The LLM request with prompt and parameters

        Yields:
            str: Streaming response chunks

        Raises:
            ProviderError: If generation fails
            ValidationError: If request is invalid
        """
        ...

    def estimate_cost(self, request: "ProtocolLLMRequest") -> float:
        """
        Estimate the cost for this request with this provider.

        Args:
            request: The LLM request to estimate cost for

        Returns:
            float: Estimated cost in USD (0.0 for local providers)
        """
        ...

    async def health_check(self) -> "ProtocolLLMHealthResponse":
        """
        Perform a health check on the provider.

        Returns:
            ProtocolLLMHealthResponse: Strongly-typed health status information
        """
        ...

    async def get_provider_info(self) -> dict[str, Any]:
        """Get comprehensive provider information."""
        ...

    def supports_streaming(self) -> bool:
        """Check if provider supports streaming responses."""
        ...

    def supports_async(self) -> bool:
        """Check if provider supports async operations."""
        ...
