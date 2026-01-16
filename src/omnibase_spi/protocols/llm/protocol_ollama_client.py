"""Protocol for Ollama client operations with local LLM models."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Protocol, runtime_checkable

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
    """Protocol for local Ollama LLM client operations.

    Defines the interface for query enhancement, answer generation,
    and conversational capabilities using local Ollama models with
    strong typing, ONEX standards compliance, and zero API costs.

    Example:
        ```python
        async def use_ollama_client(
            client: ProtocolOllamaClient,
            query: str,
            documents: list[ProtocolRetrievedDocument]
        ) -> str:
            # Check Ollama service health
            health = await client.health_check()
            if not health.is_healthy:
                raise RuntimeError("Ollama service unavailable")

            # Enhance query for better retrieval
            enhancement = await client.enhance_query(query, documents)
            print(f"Enhanced: {enhancement.enhanced_query}")

            # Generate answer from documents
            result = await client.generate_answer(
                query=enhancement.enhanced_query,
                context_documents=documents
            )

            return result.answer
        ```

    Key Features:
        - **Local Model Access**: Zero-cost local LLM operations
        - **Query Enhancement**: Intelligent query reformulation for RAG
        - **Answer Generation**: Context-aware answer synthesis
        - **Streaming Support**: Real-time response streaming
        - **Quality Validation**: Response quality scoring
        - **Model Selection**: Automatic model selection by task type
        - **Health Monitoring**: Service availability tracking

    See Also:
        - ProtocolLLMProvider: Generic provider interface
        - ProtocolOllamaCapabilities: Model capability structure
        - ProtocolQueryEnhancementResult: Query enhancement result
        - ProtocolAnswerGenerationResult: Answer generation result
    """

    async def get_available_models(self) -> list[str]:
        """Get list of available Ollama models.

        Returns:
            List of model names available on local Ollama instance

        Raises:
            ConnectionError: If Ollama service is unreachable
            TimeoutError: If request exceeds timeout

        Example:
            ```python
            models = await client.get_available_models()
            print(f"Available models: {', '.join(models)}")
            # Select best model for task
            model = client.select_best_model("analytical")
            ```
        """
        ...

    async def get_model_capabilities(
        self, model_name: str
    ) -> ProtocolOllamaCapabilities:
        """Get capabilities for a specific Ollama model.

        Args:
            model_name: Model identifier to query

        Returns:
            Model capabilities with context length and features

        Raises:
            ValueError: If model_name is invalid
            KeyError: If model not found

        Example:
            ```python
            caps = await client.get_model_capabilities("llama2")
            print(f"Context: {caps.context_length} tokens")
            print(f"Supports chat: {caps.supports_chat}")
            ```
        """
        ...

    async def health_check(self) -> ProtocolLLMHealthResponse:
        """Check health and availability of Ollama service.

        Returns:
            Health status with latency and error information

        Example:
            ```python
            health = await client.health_check()
            if health.is_healthy:
                print(f"Ollama ready (latency: {health.latency_ms}ms)")
            else:
                logger.error(f"Ollama unhealthy: {health.error_message}")
            ```
        """
        ...

    async def enhance_query(
        self,
        query: str,
        context_documents: list[ProtocolRetrievedDocument] | None = None,
    ) -> ProtocolQueryEnhancementResult:
        """Enhance a natural language query for better retrieval.

        Args:
            query: Original user query to enhance
            context_documents: Optional context documents for enhancement

        Returns:
            Query enhancement result with enhanced query and metadata

        Raises:
            ValueError: If query is empty or invalid
            ModelError: If enhancement generation fails

        Example:
            ```python
            # Basic query enhancement
            result = await client.enhance_query("python async")
            print(f"Original: {query}")
            print(f"Enhanced: {result.enhanced_query}")
            print(f"Confidence: {result.confidence_score}")

            # With context documents
            result = await client.enhance_query(query, documents)
            # Enhanced query uses document context
            ```
        """
        ...

    async def generate_answer(
        self,
        query: str,
        context_documents: list[ProtocolRetrievedDocument],
        sources: list[str] | None = None,
    ) -> ProtocolAnswerGenerationResult:
        """Generate an answer from retrieved context documents.

        Args:
            query: User's original question
            context_documents: Retrieved documents providing context
            sources: Optional source references for citation

        Returns:
            Answer generation result with generated content and metadata

        Raises:
            ValueError: If query or documents are invalid
            ModelError: If answer generation fails

        Example:
            ```python
            # Generate answer with context
            result = await client.generate_answer(
                query="What is ONEX?",
                context_documents=retrieved_docs,
                sources=["docs/architecture.md"]
            )

            print(f"Answer: {result.answer}")
            print(f"Quality: {result.quality_score}")
            print(f"Sources: {result.source_citations}")
            ```
        """
        ...

    def generate_answer_stream(
        self,
        query: str,
        context_documents: list[ProtocolRetrievedDocument],
        sources: list[str] | None = None,
    ) -> Iterator[str]:
        """Generate streaming answer from retrieved context documents.

        Args:
            query: User's original question
            context_documents: Retrieved documents providing context
            sources: Optional source references for citation

        Yields:
            Streaming answer chunks for real-time display

        Raises:
            ValueError: If query or documents are invalid
            ModelError: If streaming generation fails

        Example:
            ```python
            # Stream answer in real-time
            for chunk in client.generate_answer_stream(
                query="Explain workflow orchestration",
                context_documents=docs
            ):
                print(chunk, end="", flush=True)
            print()  # New line after streaming
            ```
        """
        ...

    def select_best_model(self, query_type: LiteralQueryType) -> str:
        """Select best Ollama model for query type.

        Args:
            query_type: Type of query (e.g., "analytical", "conversational")

        Returns:
            Model name best suited for query type

        Example:
            ```python
            # Select model by query characteristics
            model = client.select_best_model("analytical")
            print(f"Using {model} for analysis tasks")

            model = client.select_best_model("conversational")
            print(f"Using {model} for chat")
            ```
        """
        ...

    def validate_response_quality(
        self,
        question: str,
        answer: str,
        sources: list[str],
    ) -> float:
        """Validate the quality of a generated response.

        Args:
            question: Original question asked
            answer: Generated answer to validate
            sources: Source documents used for generation

        Returns:
            Quality score from 0.0 (poor) to 1.0 (excellent)

        Example:
            ```python
            result = await client.generate_answer(query, docs)
            quality = client.validate_response_quality(
                question=query,
                answer=result.answer,
                sources=result.source_citations
            )

            if quality < 0.7:
                logger.warning("Low quality answer, consider retry")
                # Retry with different model or enhanced query
            ```
        """
        ...
