"""ContractEnrichmentResult -- canonical output for context enrichment.

Captures the result of a context enrichment operation, including the
enriched summary, token budget accounting, relevance scoring, and
provenance metadata (model identity, prompt version, latency).

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ContractEnrichmentResult(BaseModel):
    """Result of a context enrichment operation.

    Produced by enrichment handlers that transform raw context (code
    snippets, documentation, conversation history) into a condensed,
    token-efficient summary suitable for LLM prompt injection.

    Adding a new ``enrichment_type`` variant requires a ``schema_version``
    bump so that consumers can detect the change.  Experimental strategies
    should be prototyped via the ``extensions`` dict before graduating to
    a first-class Literal value.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        summary_markdown: Markdown-formatted enriched summary of the context.
        token_count: Number of tokens in the enriched summary.
        relevance_score: Relevance score of the enrichment to the prompt
            (0.0 = irrelevant, 1.0 = maximally relevant).
        enrichment_type: Category of enrichment strategy applied.
        latency_ms: Wall-clock time the enrichment took, in milliseconds.
        model_used: Identifier of the model used for enrichment
            (e.g. 'qwen2.5-72b', 'gpt-4o').
        prompt_version: Version identifier of the enrichment prompt template.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    summary_markdown: str = Field(
        ...,
        min_length=1,
        description="Markdown-formatted enriched summary of the context.",
    )
    token_count: int = Field(
        ...,
        ge=0,
        description="Number of tokens in the enriched summary.",
    )
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Relevance score of the enrichment to the prompt "
            "(0.0 = irrelevant, 1.0 = maximally relevant)."
        ),
    )
    enrichment_type: Literal["code_analysis", "similarity", "summarization"] = Field(
        ...,
        description="Category of enrichment strategy applied.",
    )
    latency_ms: float = Field(
        ...,
        ge=0.0,
        description="Wall-clock time the enrichment took, in milliseconds.",
    )
    model_used: str = Field(
        ...,
        min_length=1,
        description=(
            "Identifier of the model used for enrichment "
            "(e.g. 'qwen2.5-72b', 'gpt-4o')."
        ),
    )
    prompt_version: str = Field(
        ...,
        min_length=1,
        description="Version identifier of the enrichment prompt template.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )
