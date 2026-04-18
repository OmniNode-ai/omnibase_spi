# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ContractSavingsEstimate -- tiered token-savings attribution.

Wire-format contract for estimating how much token spend the ONEX
platform saved in a given session by comparing actual costs against
a counterfactual (what the user would have spent without the platform).

Savings are broken into categories with two tiers:
- **direct** (Tier A): measurable from instrumentation (e.g. local routing).
- **heuristic** (Tier B): estimated from baselines (e.g. pattern injection,
  validator catches, delegation, RAG).

Each category carries typed evidence via a discriminated union so
consumers can audit the derivation.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class LocalRoutingEvidence(BaseModel):
    """Evidence for savings from routing calls to cheaper local models."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_type: Literal["local_routing"] = "local_routing"
    reference_model_id: str
    reference_cost_usd: float
    actual_model_id: str
    actual_cost_usd: float
    call_count: int


class PatternInjectionEvidence(BaseModel):
    """Evidence for savings from injecting learned patterns into prompts."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_type: Literal["pattern_injection"] = "pattern_injection"
    patterns_injected: int
    tokens_injected: int
    regen_multiplier: float


class ValidatorCatchEvidence(BaseModel):
    """Evidence for savings from catching errors before they reach LLM regen cycles."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_type: Literal["validator_catches"] = "validator_catches"
    catch_count: int
    catches_by_severity: dict[str, int]
    catches_by_type: dict[str, int]
    tokens_per_fix_cycle_weighted: int
    fix_cycle_baseline_version: str


class DelegationEvidence(BaseModel):
    """Evidence for savings from avoiding unnecessary subagent delegation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_type: Literal["agent_delegation"] = "agent_delegation"
    subagent_calls_avoided: int
    avg_tokens_per_call: int
    baseline_version: str


class RagEvidence(BaseModel):
    """Evidence for savings from memory/RAG retrieval avoiding regeneration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_type: Literal["memory_rag"] = "memory_rag"
    tokens_retrieved: int
    regen_tokens_estimate: int
    regen_multiplier: float
    baseline_version: str


SavingsEvidence = Annotated[
    LocalRoutingEvidence
    | PatternInjectionEvidence
    | ValidatorCatchEvidence
    | DelegationEvidence
    | RagEvidence,
    Field(discriminator="evidence_type"),
]


class ContractSavingsCategoryBreakdown(BaseModel):
    """One category of token savings with its evidence and confidence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: str
    tier: str
    tokens_saved: int
    cost_saved_usd: float
    confidence: float = Field(..., ge=0.0, le=1.0)
    method: str
    evidence: SavingsEvidence


class ContractSavingsEstimate(BaseModel):
    """Top-level savings estimate for a single session.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        session_id: Session that generated these savings.
        correlation_id: Correlation ID linking to measurement pipeline.
        timestamp_iso: ISO-8601 timestamp of the estimate.
        actual_total_tokens: Tokens actually consumed in this session.
        actual_cost_usd: Actual cost of the session.
        actual_model_id: Model used in the session.
        counterfactual_model_id: Model the user would have used without the platform.
        direct_savings_usd: Sum of cost_saved_usd for tier=="direct" categories.
        direct_tokens_saved: Sum of tokens_saved for tier=="direct" categories.
        estimated_total_savings_usd: Sum of cost_saved_usd for all categories.
        estimated_total_tokens_saved: Sum of tokens_saved for all categories.
        categories: Per-category breakdown with evidence.
        direct_confidence: Confidence of Tier A (direct) savings.
        heuristic_confidence_avg: Cost-weighted avg confidence of Tier B categories.
        estimation_method: Algorithm used to produce the estimate.
        treatment_group: A/B test group ("treatment" or "control").
        is_measured: True if this estimate is backed by A/B measurement.
        measurement_basis: Description of how measurement was done.
        baseline_session_id: Session ID of the control baseline (if measured).
        pricing_manifest_version: Version of the pricing manifest used.
        completeness_status: "complete", "phase_limited", or "partial".
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"  # string-version-ok: wire format
    session_id: str
    correlation_id: str
    timestamp_iso: str
    actual_total_tokens: int
    actual_cost_usd: float
    actual_model_id: str
    counterfactual_model_id: str
    direct_savings_usd: float
    direct_tokens_saved: int
    estimated_total_savings_usd: float
    estimated_total_tokens_saved: int
    categories: list[ContractSavingsCategoryBreakdown]
    direct_confidence: float = Field(..., ge=0.0, le=1.0)
    heuristic_confidence_avg: float = Field(..., ge=0.0, le=1.0)
    estimation_method: str
    treatment_group: str
    is_measured: bool = False
    measurement_basis: str = ""
    baseline_session_id: str = ""
    pricing_manifest_version: str = ""
    completeness_status: str = "complete"
    extensions: dict[str, Any] = Field(default_factory=dict)
