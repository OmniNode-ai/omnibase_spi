"""ContractLlmCallMetrics -- per-call LLM cost and usage tracking.

Provides detailed metrics for a single LLM API call, including token
counts, cost estimation, latency, and usage normalization.  Separates
raw provider data from a canonical normalized representation so that
downstream consumers never depend on provider-specific wire formats.

Extends the aggregate ``ContractCostMetrics`` (OMN-2024) with per-call
granularity and provider-level provenance tracking.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from omnibase_spi.contracts.measurement.enum_usage_source import (
    ContractEnumUsageSource,
)

# -- Usage normalization layer -----------------------------------------------


class ContractLlmUsageRaw(BaseModel):
    """Raw provider wire format for LLM usage data.

    Stores the verbatim JSON payload returned by the provider API.
    This is intentionally unstructured: providers differ in what they
    report, and we preserve the original data for auditing.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        provider: Provider identifier (e.g. 'openai', 'anthropic', 'vllm').
        raw_data: Verbatim provider response data stored as JSON-compatible dict.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    provider: str = Field(
        default="",
        description="Provider identifier (e.g. 'openai', 'anthropic', 'vllm').",
    )
    raw_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Verbatim provider response data stored as JSON-compatible dict.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )


class ContractLlmUsageNormalized(BaseModel):
    """Canonical normalized form for LLM token usage.

    Downstream consumers always work with this form rather than raw
    provider data.  The ``source`` field indicates whether the counts
    come from the API, were estimated locally, or are missing.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        prompt_tokens: Number of prompt (input) tokens.
        completion_tokens: Number of completion (output) tokens.
        total_tokens: Total tokens (prompt + completion).
        source: Provenance of the usage data.
        usage_is_estimated: True when tokens were counted locally rather
            than reported by the provider API.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    prompt_tokens: int = Field(
        default=0,
        ge=0,
        description="Number of prompt (input) tokens.",
    )
    completion_tokens: int = Field(
        default=0,
        ge=0,
        description="Number of completion (output) tokens.",
    )
    total_tokens: int = Field(
        default=0,
        ge=0,
        description="Total tokens (prompt + completion).",
    )
    source: ContractEnumUsageSource = Field(
        default=ContractEnumUsageSource.MISSING,
        description="Provenance of the usage data.",
    )
    usage_is_estimated: bool = Field(
        default=False,
        description=(
            "True when tokens were counted locally rather than "
            "reported by the provider API."
        ),
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )

    @model_validator(mode="after")
    def _validate_consistency(self) -> ContractLlmUsageNormalized:
        """Ensure usage_is_estimated is consistent with source and token sum.

        When source is ESTIMATED, usage_is_estimated must be True.
        When source is API, usage_is_estimated must be False.
        total_tokens must equal prompt_tokens + completion_tokens.
        """
        if (
            self.source == ContractEnumUsageSource.ESTIMATED
            and not self.usage_is_estimated
        ):
            raise ValueError(
                "usage_is_estimated must be True when source is 'estimated'"
            )
        if self.source == ContractEnumUsageSource.API and self.usage_is_estimated:
            raise ValueError("usage_is_estimated must be False when source is 'api'")
        expected = self.prompt_tokens + self.completion_tokens
        if self.total_tokens != expected:
            raise ValueError(
                f"total_tokens ({self.total_tokens}) must equal "
                f"prompt_tokens + completion_tokens ({expected})"
            )
        return self


# -- Primary contract --------------------------------------------------------


class ContractLlmCallMetrics(BaseModel):
    """Metrics for a single LLM API call.

    Captures model identity, token counts, cost estimation, latency,
    and usage normalization for one LLM invocation.  Multiple instances
    of this contract aggregate into ``ContractCostMetrics`` at the
    phase level.

    The top-level ``usage_is_estimated`` flag is intentionally independent
    of ``usage_normalized.usage_is_estimated``.  When the normalized layer
    is absent the top-level flag still conveys estimation provenance;
    when both are present callers should prefer the normalized value.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        model_id: Identifier of the LLM model used (e.g. 'gpt-4o', 'claude-opus-4-20250514').
        prompt_tokens: Number of prompt (input) tokens.
        completion_tokens: Number of completion (output) tokens.
        total_tokens: Total tokens (prompt + completion).
        estimated_cost_usd: Estimated cost in USD for this call.
        latency_ms: End-to-end latency in milliseconds.
        usage_raw: Raw provider usage data (verbatim API response).
        usage_normalized: Canonical normalized usage data.
        usage_is_estimated: True when tokens were counted locally rather
            than reported by the provider API.  Independent of the
            nested ``usage_normalized.usage_is_estimated`` flag.
        input_hash: Hash of the input data for reproducibility tracking.
            Expected format is algorithm-prefixed hex (e.g. ``sha256-a1b2...``).
        code_version: Version of the calling code.
        contract_version: Version of this contract schema.
        timestamp_iso: ISO-8601 timestamp of the call (e.g.
            ``2026-02-15T10:00:00Z``).  Plain string for wire-format
            flexibility.
        source: Provenance label for this metrics record.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    model_id: str = Field(
        ...,
        description="Identifier of the LLM model used (e.g. 'gpt-4o', 'claude-opus-4-20250514').",
    )
    prompt_tokens: int = Field(
        default=0,
        ge=0,
        description="Number of prompt (input) tokens.",
    )
    completion_tokens: int = Field(
        default=0,
        ge=0,
        description="Number of completion (output) tokens.",
    )
    total_tokens: int = Field(
        default=0,
        ge=0,
        description="Total tokens (prompt + completion).",
    )
    estimated_cost_usd: float | None = Field(
        default=None,
        ge=0.0,
        description="Estimated cost in USD for this call.",
    )
    latency_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="End-to-end latency in milliseconds.",
    )

    # Usage normalization
    usage_raw: ContractLlmUsageRaw | None = Field(
        default=None,
        description="Raw provider usage data (verbatim API response).",
    )
    usage_normalized: ContractLlmUsageNormalized | None = Field(
        default=None,
        description="Canonical normalized usage data.",
    )
    usage_is_estimated: bool = Field(
        default=False,
        description=(
            "True when tokens were counted locally rather than "
            "reported by the provider API.  This is a top-level summary "
            "flag independent of usage_normalized.usage_is_estimated; "
            "callers may set them independently when the normalized "
            "layer is absent."
        ),
    )

    # Global invariant fields
    input_hash: str = Field(
        default="",
        description=(
            "Hash of the input data for reproducibility tracking.  "
            "Expected format is algorithm-prefixed hex, e.g. "
            "'sha256-a1b2c3...'.  No validation is enforced; producers "
            "should follow this convention for interoperability."
        ),
    )
    code_version: str = Field(
        default="",
        description="Version of the calling code.",
    )
    contract_version: str = Field(
        default="1.0",
        description="Version of this contract schema.",
    )
    timestamp_iso: str = Field(
        default="",
        description=(
            "ISO-8601 timestamp of the call (e.g. '2026-02-15T10:00:00Z').  "
            "Kept as a plain string for wire-format flexibility; producers "
            "should emit full ISO-8601 with timezone designator."
        ),
    )
    source: str = Field(
        default="",
        description="Provenance label for this metrics record.",
    )

    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )

    @model_validator(mode="after")
    def _validate_token_consistency(self) -> ContractLlmCallMetrics:
        """Ensure token fields are internally consistent.

        Checks:
        1. total_tokens == prompt_tokens + completion_tokens (always).
        2. When usage_normalized is present, its token counts must match
           the top-level prompt_tokens, completion_tokens, and
           total_tokens.  This prevents silent divergence between the
           summary fields and the canonical normalized representation.
        """
        expected = self.prompt_tokens + self.completion_tokens
        if self.total_tokens != expected:
            raise ValueError(
                f"total_tokens ({self.total_tokens}) must equal "
                f"prompt_tokens + completion_tokens ({expected})"
            )

        if self.usage_normalized is not None:
            norm = self.usage_normalized
            mismatches: list[str] = []
            if self.prompt_tokens != norm.prompt_tokens:
                mismatches.append(
                    f"prompt_tokens: top-level={self.prompt_tokens} "
                    f"vs normalized={norm.prompt_tokens}"
                )
            if self.completion_tokens != norm.completion_tokens:
                mismatches.append(
                    f"completion_tokens: top-level={self.completion_tokens} "
                    f"vs normalized={norm.completion_tokens}"
                )
            if self.total_tokens != norm.total_tokens:
                mismatches.append(
                    f"total_tokens: top-level={self.total_tokens} "
                    f"vs normalized={norm.total_tokens}"
                )
            if mismatches:
                raise ValueError(
                    "Top-level token counts disagree with "
                    "usage_normalized: " + "; ".join(mismatches)
                )

        return self
