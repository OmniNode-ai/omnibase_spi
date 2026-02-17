"""Protocol for context enrichment operations.

This module defines the protocol for enriching LLM prompts with
relevant context from code analysis, similarity search, or
summarization.  Implementations transform raw context (code snippets,
documentation, conversation history) into condensed, token-efficient
summaries suitable for prompt injection.

Example:
    >>> class MyEnricher:
    ...     async def enrich(
    ...         self, prompt: str, context: str
    ...     ) -> ContractEnrichmentResult:
    ...         # Implementation here
    ...         ...
    >>>
    >>> # Check protocol compliance
    >>> assert isinstance(MyEnricher(), ProtocolContextEnrichment)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.enrichment.contract_enrichment_result import (
        ContractEnrichmentResult,
    )

__all__ = ["ProtocolContextEnrichment"]


@runtime_checkable
class ProtocolContextEnrichment(Protocol):
    """Protocol for context enrichment operations.

    Defines the interface for enriching LLM prompts with relevant
    context.  Implementations should analyze the provided context,
    extract relevant information, and produce a condensed summary
    with relevance scoring and token budget accounting.

    The protocol supports three enrichment strategies:
    - code_analysis: Static analysis of code structure and semantics
    - similarity: Vector similarity search against a knowledge base
    - summarization: LLM-based summarization of raw context

    Example:
        >>> async def example():
        ...     enricher: ProtocolContextEnrichment = get_enricher()
        ...     result = await enricher.enrich(prompt, context)
        ...     print(f"Tokens: {result.token_count}, Relevance: {result.relevance_score}")
    """

    async def enrich(
        self,
        prompt: str,
        context: str,
    ) -> ContractEnrichmentResult:
        """Enrich a prompt with relevant context.

        Analyzes the provided context in relation to the prompt and
        produces a condensed, token-efficient summary suitable for
        LLM prompt injection.

        This method intentionally accepts raw strings rather than structured
        input models (unlike sibling protocols such as ProtocolIntentClassifier)
        because enrichment is designed as a simple, composable transformation.
        Callers that need correlation IDs, metadata, or retry policies should
        wrap this call at the orchestration layer.

        Args:
            prompt: The user prompt or query to enrich with context.
            context: Raw context material (code snippets, documentation,
                conversation history, etc.) to analyze and summarize.

        Returns:
            Enrichment result containing:
                - summary_markdown: Condensed context summary
                - token_count: Token budget consumed
                - relevance_score: How relevant the context is (0.0-1.0)
                - enrichment_type: Strategy used (code_analysis/similarity/summarization)
                - latency_ms: Processing time
                - model_used: Which model performed the enrichment
                - prompt_version: Version of the enrichment prompt template

        Raises:
            SPIError: Implementations should raise subclasses of
                ``omnibase_spi.exceptions.SPIError`` for invalid input,
                model failures, or timeout conditions.
        """
        ...
