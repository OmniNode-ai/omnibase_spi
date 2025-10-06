"""
LLM (Large Language Model) types for ONEX SPI interfaces.

This module defines protocol types for LLM operations including model providers,
query processing, conversation management, and health monitoring.

All types follow the zero-dependency principle and use strong typing without Any.
"""

from typing import Any, List, Optional, Protocol, runtime_checkable

# Enum-like types for LLM operations
LiteralQueryType = str
LiteralLLMProvider = str


@runtime_checkable
class ProtocolLLMHealthResponse(Protocol):
    """
    Protocol for LLM health check responses.

    This protocol defines the contract for health check results from LLM providers,
    including status information, performance metrics, and capability reports.
    """

    @property
    def is_healthy(self) -> bool:
        """Whether the LLM provider is healthy."""
        ...

    @property
    def provider_name(self) -> str:
        """Name of the LLM provider."""
        ...

    @property
    def response_time_ms(self) -> float:
        """Response time in milliseconds."""
        ...

    @property
    def available_models(self) -> List[str]:
        """List of available models."""
        ...

    @property
    def error_message(self) -> Optional[str]:
        """Error message if health check failed."""
        ...


@runtime_checkable
class ProtocolLLMRequest(Protocol):
    """
    Protocol for LLM generation requests.

    This protocol defines the contract for requests to LLM providers,
    including the prompt, parameters, and generation settings.
    """

    @property
    def prompt(self) -> str:
        """The main prompt or query."""
        ...

    @property
    def model_name(self) -> str:
        """Name of the model to use."""
        ...

    @property
    def parameters(self) -> dict[str, Any]:
        """Generation parameters."""
        ...

    @property
    def max_tokens(self) -> Optional[int]:
        """Maximum tokens to generate."""
        ...

    @property
    def temperature(self) -> Optional[float]:
        """Temperature for generation."""
        ...


@runtime_checkable
class ProtocolLLMResponse(Protocol):
    """
    Protocol for LLM generation responses.

    This protocol defines the contract for responses from LLM providers,
    including the generated text, usage statistics, and metadata.
    """

    @property
    def generated_text(self) -> str:
        """The generated text."""
        ...

    @property
    def model_used(self) -> str:
        """Model that was used."""
        ...

    @property
    def usage_statistics(self) -> dict[str, Any]:
        """Usage statistics (tokens, time, etc.)."""
        ...

    @property
    def finish_reason(self) -> str:
        """Reason generation finished."""
        ...

    @property
    def response_metadata(self) -> dict[str, Any]:
        """Additional response metadata."""
        ...


@runtime_checkable
class ProtocolModelCapabilities(Protocol):
    """
    Protocol for model capability descriptions.

    This protocol defines the contract for describing model capabilities,
    including supported features, input/output formats, and limitations.
    """

    @property
    def model_name(self) -> str:
        """Name of the model."""
        ...

    @property
    def supports_streaming(self) -> bool:
        """Whether the model supports streaming."""
        ...

    @property
    def supports_function_calling(self) -> bool:
        """Whether the model supports function calling."""
        ...

    @property
    def max_context_length(self) -> int:
        """Maximum context length."""
        ...

    @property
    def supported_modalities(self) -> list[str]:
        """Supported input/output modalities."""
        ...


@runtime_checkable
class ProtocolProviderConfig(Protocol):
    """
    Protocol for LLM provider configuration.

    This protocol defines the contract for provider configuration,
    including API settings, model preferences, and connection parameters.
    """

    @property
    def provider_name(self) -> str:
        """Name of the provider."""
        ...

    @property
    def api_key(self) -> Optional[str]:
        """API key for authentication."""
        ...

    @property
    def base_url(self) -> Optional[str]:
        """Base URL for API calls."""
        ...

    @property
    def default_model(self) -> str:
        """Default model to use."""
        ...

    async def connection_timeout(self) -> int:
        """Connection timeout in seconds."""
        ...


@runtime_checkable
class ProtocolAnswerGenerationResult(Protocol):
    """
    Protocol for answer generation results.

    This protocol defines the contract for results from answer generation operations,
    including the generated answer, confidence scores, and source references.
    """

    @property
    def answer(self) -> str:
        """The generated answer."""
        ...

    @property
    def confidence_score(self) -> float:
        """Confidence score for the answer."""
        ...

    @property
    def source_documents(self) -> list[dict[str, Any]]:
        """Source documents used for generation."""
        ...

    @property
    def generation_metadata(self) -> dict[str, Any]:
        """Metadata about the generation process."""
        ...


@runtime_checkable
class ProtocolConversationContext(Protocol):
    """
    Protocol for conversation context management.

    This protocol defines the contract for conversation context,
    including message history, context management, and session tracking.
    """

    @property
    def conversation_id(self) -> str:
        """Unique conversation identifier."""
        ...

    @property
    def messages(self) -> list[dict[str, Any]]:
        """Conversation message history."""
        ...

    @property
    def context_window(self) -> int:
        """Context window size."""
        ...

    @property
    def system_prompt(self) -> Optional[str]:
        """System prompt for the conversation."""
        ...


@runtime_checkable
class ProtocolOllamaCapabilities(Protocol):
    """
    Protocol for Ollama-specific capabilities.

    This protocol defines the contract for Ollama-specific capabilities
    and configuration options.
    """

    @property
    def supports_gpu(self) -> bool:
        """Whether GPU acceleration is supported."""
        ...

    @property
    def available_models(self) -> list[str]:
        """List of available Ollama models."""
        ...

    @property
    def ollama_version(self) -> str:
        """Ollama server version."""
        ...

    @property
    def system_info(self) -> dict[str, Any]:
        """System information."""
        ...


@runtime_checkable
class ProtocolQueryEnhancementResult(Protocol):
    """
    Protocol for query enhancement results.

    This protocol defines the contract for query enhancement operations,
    including the enhanced query, expansion terms, and relevance scores.
    """

    async def original_query(self) -> str:
        """The original query."""
        ...

    async def enhanced_query(self) -> str:
        """The enhanced query."""
        ...

    @property
    def expansion_terms(self) -> list[str]:
        """Terms added during expansion."""
        ...

    @property
    def relevance_score(self) -> float:
        """Relevance score for the enhancement."""
        ...

    @property
    def enhancement_metadata(self) -> dict[str, Any]:
        """Metadata about the enhancement process."""
        ...


@runtime_checkable
class ProtocolRetrievedDocument(Protocol):
    """
    Protocol for retrieved documents in context.

    This protocol defines the contract for documents retrieved during
    search operations for use in LLM context.
    """

    @property
    def document_id(self) -> str:
        """Unique document identifier."""
        ...

    @property
    def content(self) -> str:
        """Document content."""
        ...

    @property
    def metadata(self) -> dict[str, Any]:
        """Document metadata."""
        ...

    @property
    def relevance_score(self) -> float:
        """Relevance score for the document."""
        ...


# Type aliases for backward compatibility and convenience
LLMHealthResponse = ProtocolLLMHealthResponse
LLMRequest = ProtocolLLMRequest
LLMResponse = ProtocolLLMResponse
ModelCapabilities = ProtocolModelCapabilities
ProviderConfig = ProtocolProviderConfig
AnswerGenerationResult = ProtocolAnswerGenerationResult
ConversationContext = ProtocolConversationContext
OllamaCapabilities = ProtocolOllamaCapabilities
QueryEnhancementResult = ProtocolQueryEnhancementResult
RetrievedDocument = ProtocolRetrievedDocument

__all__ = [
    "LiteralQueryType",
    "LiteralLLMProvider",
    "ProtocolLLMHealthResponse",
    "ProtocolLLMRequest",
    "ProtocolLLMResponse",
    "ProtocolModelCapabilities",
    "ProtocolProviderConfig",
    "ProtocolAnswerGenerationResult",
    "ProtocolConversationContext",
    "ProtocolOllamaCapabilities",
    "ProtocolQueryEnhancementResult",
    "ProtocolRetrievedDocument",
    "LLMHealthResponse",
    "LLMRequest",
    "LLMResponse",
    "ModelCapabilities",
    "ProviderConfig",
    "AnswerGenerationResult",
    "ConversationContext",
    "OllamaCapabilities",
    "QueryEnhancementResult",
    "RetrievedDocument",
]
