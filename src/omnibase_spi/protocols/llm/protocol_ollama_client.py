from typing import TYPE_CHECKING, Any, Iterator, Protocol, runtime_checkable

"""
Protocol interface for Ollama client operations.

Defines the standard interface for interacting with Ollama local LLM models
for query enhancement, answer generation, and conversational capabilities.
"""

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_llm_types import (
        LiteralQueryType,
        ProtocolAnswerGenerationResult,
        ProtocolLLMHealthResponse,
        ProtocolOllamaCapabilities,
        ProtocolQueryEnhancementResult,
        ProtocolRetrievedDocument,
    )


@runtime_checkable
class ProtocolOllamaClient(Protocol):
    """
    Protocol for Ollama client operations.

    Defines the interface for query enhancement, answer generation,
    and conversational capabilities using local Ollama models with
    strong typing and ONEX standards compliance.
    """

    async def get_available_models(self) -> list[str]: ...
    async def get_model_capabilities(
        self, model_name: str
    ) -> "ProtocolOllamaCapabilities":
        """Get capabilities for a specific model."""
        ...

    async def health_check(self) -> "ProtocolLLMHealthResponse":
        """Check health and availability of Ollama service."""
        ...

    async def enhance_query(
        self,
        query: str,
        context_documents: list["ProtocolRetrievedDocument"] | None = None,
    ) -> "ProtocolQueryEnhancementResult":
        """
        Enhance a natural language query for better retrieval.

        Args:
            query: Original user query
            context_documents: Optional context documents for enhancement

        Returns:
            Query enhancement result with enhanced query and metadata
        """
        ...

    async def generate_answer(
        self,
        query: str,
        context_documents: list["ProtocolRetrievedDocument"],
        sources: list[str] | None = None,
    ) -> "ProtocolAnswerGenerationResult":
        """
        Generate an answer from retrieved context documents.

        Args:
            query: User's original question
            context_documents: Retrieved documents providing context
            sources: Optional source references for citation

        Returns:
            Answer generation result with generated content and metadata
        """
        ...

    def generate_answer_stream(
        self,
        query: str,
        context_documents: list["ProtocolRetrievedDocument"],
        sources: list[str] | None = None,
    ) -> Iterator[str]:
        """
        Generate streaming answer from retrieved context documents.

        Args:
            query: User's original question
            context_documents: Retrieved documents providing context
            sources: Optional source references for citation

        Yields:
            Streaming answer chunks
        """
        ...

    def select_best_model(self, query_type: "LiteralQueryType") -> str: ...
    def validate_response_quality(
        self,
        question: str,
        answer: str,
        sources: list[str],
    ) -> float:
        """
        Validate the quality of a generated response.

        Args:
            question: Original question
                ...
            answer: Generated answer
            sources: Source documents used

        Returns:
            Quality score (0.0 to 1.0)
        """
        ...
