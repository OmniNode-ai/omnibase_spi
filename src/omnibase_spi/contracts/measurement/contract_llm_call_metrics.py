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

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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

    The top-level ``usage_is_estimated`` flag conveys estimation provenance
    even when ``usage_normalized`` is absent.  When both are present the
    two flags must agree; a ``ValueError`` is raised if they disagree to
    prevent inconsistent records.

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
            than reported by the provider API.  When ``usage_normalized``
            is present, this flag must agree with
            ``usage_normalized.usage_is_estimated``; a ``ValueError`` is
            raised if they disagree.
        input_hash: Hash of the input data for reproducibility tracking.
            Expected format is algorithm-prefixed hex (e.g. ``sha256-a1b2...``).
        code_version: Version of the calling code.
        contract_version: Version of this contract schema.
        timestamp_iso: ISO-8601 timestamp of the call (e.g.
            ``2026-02-15T10:00:00Z``).  Plain string for wire-format
            flexibility.
        reporting_source: Provenance/origin label for this metrics record
            (e.g. 'pipeline-agent', 'batch-ingest').  Named ``reporting_source``
            to avoid confusion with ``usage_normalized.source`` which carries
            a different type (``ContractEnumUsageSource``).
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    model_id: str = Field(
        ...,
        min_length=1,
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
            "reported by the provider API.  When usage_normalized is "
            "present this flag must agree with "
            "usage_normalized.usage_is_estimated."
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
    reporting_source: str = Field(
        default="",
        description=(
            "Provenance/origin label for this metrics record "
            "(e.g. 'pipeline-agent', 'batch-ingest').  Named "
            "'reporting_source' to avoid confusion with "
            "usage_normalized.source (ContractEnumUsageSource)."
        ),
    )

    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )

    @field_validator("timestamp_iso")
    @classmethod
    def _validate_timestamp_iso(cls, v: str) -> str:
        """Validate that non-empty timestamp_iso is a parseable ISO-8601 string.

        Empty strings are allowed (it is the field default).  Non-empty
        values are validated using ``datetime.fromisoformat()`` which
        accepts standard ISO-8601 formats including timezone designators.
        """
        if v == "":
            return v
        try:
            datetime.fromisoformat(v)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"timestamp_iso must be a valid ISO-8601 datetime string, "
                f"got {v!r}: {exc}"
            ) from exc
        return v

    @model_validator(mode="after")
    def _validate_token_consistency(self) -> ContractLlmCallMetrics:
        """Ensure token fields and estimation flags are internally consistent.

        Checks:
        1. total_tokens == prompt_tokens + completion_tokens (always).
        2. When usage_normalized is present, its token counts must match
           the top-level prompt_tokens, completion_tokens, and
           total_tokens.  This prevents silent divergence between the
           summary fields and the canonical normalized representation.
        3. When usage_normalized is present, the top-level
           usage_is_estimated must agree with
           usage_normalized.usage_is_estimated.
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

            if self.usage_is_estimated != norm.usage_is_estimated:
                raise ValueError(
                    f"Top-level usage_is_estimated ({self.usage_is_estimated}) "
                    f"disagrees with usage_normalized.usage_is_estimated "
                    f"({norm.usage_is_estimated}); they must be consistent "
                    f"when both are present"
                )

        return self
