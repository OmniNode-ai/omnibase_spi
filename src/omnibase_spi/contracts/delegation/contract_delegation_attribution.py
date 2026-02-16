"""ContractDelegationAttribution -- provenance for a delegated LLM call.

Records which model produced a delegation response, the endpoint used,
latency, prompt version, and the router's confidence in the delegation
decision.  Attached to every :class:`ContractDelegatedResponse` for
closed-loop attribution tracking.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ContractDelegationAttribution(BaseModel):
    """Provenance metadata for a delegated LLM response.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        model_name: Identifier of the LLM model that produced the response
            (e.g. 'qwen2.5-coder-14b', 'claude-opus-4-20250514').
        endpoint_url: URL of the LLM endpoint that was called.
            URL format validation is deferred to consumers.
        latency_ms: End-to-end latency of the LLM call in milliseconds.
        prompt_version: Version identifier for the prompt template used.
        delegation_confidence: Router confidence in the delegation decision
            (0.0-1.0).
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    model_name: str = Field(
        ...,
        min_length=1,
        description=(
            "Identifier of the LLM model that produced the response "
            "(e.g. 'qwen2.5-coder-14b', 'claude-opus-4-20250514')."
        ),
    )
    endpoint_url: str = Field(
        ...,
        min_length=1,
        description=(
            "URL of the LLM endpoint that was called.  "
            "URL format validation is deferred to consumers."
        ),
    )
    latency_ms: float = Field(
        ...,
        ge=0.0,
        description="End-to-end latency of the LLM call in milliseconds.",
    )
    prompt_version: str = Field(
        default="",
        description="Version identifier for the prompt template used.",
    )
    delegation_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Router confidence in the delegation decision (0.0-1.0).",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )
