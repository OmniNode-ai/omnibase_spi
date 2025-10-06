"""
Protocol for LLM tool provider.

Defines the interface for providing LLM tools including model router and providers
without direct imports, enabling proper dependency injection and registry patterns.
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Forward reference for LLM provider to maintain namespace isolation
    @runtime_checkable
    class ProtocolLLMProviderImpl(Protocol):
        """Protocol for LLM provider functionality."""

        pass


@runtime_checkable
class ProtocolModelRouter(Protocol):
    """Protocol for model router functionality."""

    async def generate(self, request: Any) -> Any:
        """Generate response using the model router."""
        ...

    async def get_available_providers(self) -> list[str]:
        """Get list[Any]of available providers."""
        ...


@runtime_checkable
class ProtocolLLMToolProvider(Protocol):
    """Protocol for providing LLM tools including model router and providers."""

    async def get_model_router(self) -> "ProtocolModelRouter":
        """Get configured model router with registered providers."""
        ...

    async def get_gemini_provider(self) -> "ProtocolLLMProviderImpl":
        """Get Gemini LLM provider."""
        ...

    async def get_openai_provider(self) -> "ProtocolLLMProviderImpl":
        """Get OpenAI LLM provider."""
        ...

    async def get_ollama_provider(self) -> "ProtocolLLMProviderImpl":
        """Get Ollama LLM provider."""
        ...

    async def get_claude_provider(self) -> "ProtocolLLMProviderImpl":
        """Get Claude LLM provider."""
        ...
