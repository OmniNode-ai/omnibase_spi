# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for ContractSavingsEstimate and related evidence models.

Covers:
- Frozen immutability
- extra="forbid" rejects unknown fields
- Evidence discriminator dispatches to correct type
- direct_savings_usd must equal sum of categories where tier=="direct"
- estimated_total_savings_usd must equal sum of all categories
- direct_confidence reflects Tier A category confidence
- heuristic_confidence_avg is cost-weighted average of Tier B categories only
- Confidence bounds: all values in [0.0, 1.0]
- Completeness status semantics
- JSON round-trip serialization
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.measurement.contract_savings_estimate import (
    ContractSavingsCategoryBreakdown,
    ContractSavingsEstimate,
    DelegationEvidence,
    LocalRoutingEvidence,
    PatternInjectionEvidence,
    RagEvidence,
    ValidatorCatchEvidence,
)

# ---------------------------------------------------------------------------
# Evidence models
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLocalRoutingEvidence:
    """Tests for LocalRoutingEvidence."""

    def test_create(self) -> None:
        e = LocalRoutingEvidence(
            reference_model_id="claude-opus-4-20250514",
            reference_cost_usd=0.10,
            actual_model_id="qwen3-coder-30b",
            actual_cost_usd=0.002,
            call_count=5,
        )
        assert e.evidence_type == "local_routing"
        assert e.call_count == 5

    def test_frozen(self) -> None:
        e = LocalRoutingEvidence(
            reference_model_id="x",
            reference_cost_usd=0.1,
            actual_model_id="y",
            actual_cost_usd=0.01,
            call_count=1,
        )
        with pytest.raises(ValidationError):
            e.call_count = 2  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            LocalRoutingEvidence(
                reference_model_id="x",
                reference_cost_usd=0.1,
                actual_model_id="y",
                actual_cost_usd=0.01,
                call_count=1,
                bad="no",  # type: ignore[call-arg]
            )


@pytest.mark.unit
class TestPatternInjectionEvidence:
    """Tests for PatternInjectionEvidence."""

    def test_create(self) -> None:
        e = PatternInjectionEvidence(
            patterns_injected=3,
            tokens_injected=500,
            regen_multiplier=2.5,
        )
        assert e.evidence_type == "pattern_injection"
        assert e.regen_multiplier == 2.5

    def test_frozen(self) -> None:
        e = PatternInjectionEvidence(
            patterns_injected=1, tokens_injected=100, regen_multiplier=2.0
        )
        with pytest.raises(ValidationError):
            e.patterns_injected = 5  # type: ignore[misc]


@pytest.mark.unit
class TestValidatorCatchEvidence:
    """Tests for ValidatorCatchEvidence."""

    def test_create(self) -> None:
        e = ValidatorCatchEvidence(
            catch_count=10,
            catches_by_severity={"error": 3, "warning": 7},
            catches_by_type={"type_mismatch": 5, "missing_field": 5},
            tokens_per_fix_cycle_weighted=1500,
            fix_cycle_baseline_version="v1.0",
        )
        assert e.evidence_type == "validator_catches"
        assert e.catch_count == 10

    def test_frozen(self) -> None:
        e = ValidatorCatchEvidence(
            catch_count=1,
            catches_by_severity={},
            catches_by_type={},
            tokens_per_fix_cycle_weighted=100,
            fix_cycle_baseline_version="v1",
        )
        with pytest.raises(ValidationError):
            e.catch_count = 2  # type: ignore[misc]


@pytest.mark.unit
class TestDelegationEvidence:
    """Tests for DelegationEvidence."""

    def test_create(self) -> None:
        e = DelegationEvidence(
            subagent_calls_avoided=3,
            avg_tokens_per_call=2000,
            baseline_version="v1.0",
        )
        assert e.evidence_type == "agent_delegation"


@pytest.mark.unit
class TestRagEvidence:
    """Tests for RagEvidence."""

    def test_create(self) -> None:
        e = RagEvidence(
            tokens_retrieved=1000,
            regen_tokens_estimate=3000,
            regen_multiplier=3.0,
            baseline_version="v1.0",
        )
        assert e.evidence_type == "memory_rag"
        assert e.regen_multiplier == 3.0


# ---------------------------------------------------------------------------
# ContractSavingsCategoryBreakdown
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractSavingsCategoryBreakdown:
    """Tests for ContractSavingsCategoryBreakdown."""

    def test_create(self) -> None:
        cb = ContractSavingsCategoryBreakdown(
            category="local_routing",
            tier="direct",
            tokens_saved=5000,
            cost_saved_usd=0.08,
            confidence=0.95,
            method="reference_pricing",
            evidence=LocalRoutingEvidence(
                reference_model_id="claude-opus-4-20250514",
                reference_cost_usd=0.10,
                actual_model_id="qwen3-coder-30b",
                actual_cost_usd=0.002,
                call_count=5,
            ),
        )
        assert cb.category == "local_routing"
        assert cb.tier == "direct"

    def test_frozen(self) -> None:
        cb = ContractSavingsCategoryBreakdown(
            category="local_routing",
            tier="direct",
            tokens_saved=100,
            cost_saved_usd=0.01,
            confidence=0.9,
            method="reference_pricing",
            evidence=LocalRoutingEvidence(
                reference_model_id="x",
                reference_cost_usd=0.1,
                actual_model_id="y",
                actual_cost_usd=0.01,
                call_count=1,
            ),
        )
        with pytest.raises(ValidationError):
            cb.category = "changed"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractSavingsCategoryBreakdown(
                category="local_routing",
                tier="direct",
                tokens_saved=100,
                cost_saved_usd=0.01,
                confidence=0.9,
                method="reference_pricing",
                evidence=LocalRoutingEvidence(
                    reference_model_id="x",
                    reference_cost_usd=0.1,
                    actual_model_id="y",
                    actual_cost_usd=0.01,
                    call_count=1,
                ),
                bad="no",  # type: ignore[call-arg]
            )

    def test_evidence_discriminator_local_routing(self) -> None:
        cb = ContractSavingsCategoryBreakdown(
            category="local_routing",
            tier="direct",
            tokens_saved=100,
            cost_saved_usd=0.01,
            confidence=0.9,
            method="reference_pricing",
            evidence=LocalRoutingEvidence(
                reference_model_id="x",
                reference_cost_usd=0.1,
                actual_model_id="y",
                actual_cost_usd=0.01,
                call_count=1,
            ),
        )
        assert isinstance(cb.evidence, LocalRoutingEvidence)

    def test_evidence_discriminator_validator_catches(self) -> None:
        cb = ContractSavingsCategoryBreakdown(
            category="validator_catches",
            tier="heuristic",
            tokens_saved=15000,
            cost_saved_usd=0.05,
            confidence=0.7,
            method="counted_catches",
            evidence=ValidatorCatchEvidence(
                catch_count=10,
                catches_by_severity={"error": 10},
                catches_by_type={"type_mismatch": 10},
                tokens_per_fix_cycle_weighted=1500,
                fix_cycle_baseline_version="v1.0",
            ),
        )
        assert isinstance(cb.evidence, ValidatorCatchEvidence)

    def test_evidence_discriminator_pattern_injection(self) -> None:
        cb = ContractSavingsCategoryBreakdown(
            category="pattern_injection",
            tier="heuristic",
            tokens_saved=1250,
            cost_saved_usd=0.02,
            confidence=0.6,
            method="historical_baseline",
            evidence=PatternInjectionEvidence(
                patterns_injected=3,
                tokens_injected=500,
                regen_multiplier=2.5,
            ),
        )
        assert isinstance(cb.evidence, PatternInjectionEvidence)

    def test_evidence_discriminator_delegation(self) -> None:
        cb = ContractSavingsCategoryBreakdown(
            category="agent_delegation",
            tier="heuristic",
            tokens_saved=6000,
            cost_saved_usd=0.03,
            confidence=0.5,
            method="historical_baseline",
            evidence=DelegationEvidence(
                subagent_calls_avoided=3,
                avg_tokens_per_call=2000,
                baseline_version="v1.0",
            ),
        )
        assert isinstance(cb.evidence, DelegationEvidence)

    def test_evidence_discriminator_rag(self) -> None:
        cb = ContractSavingsCategoryBreakdown(
            category="memory_rag",
            tier="heuristic",
            tokens_saved=2000,
            cost_saved_usd=0.01,
            confidence=0.5,
            method="historical_baseline",
            evidence=RagEvidence(
                tokens_retrieved=1000,
                regen_tokens_estimate=3000,
                regen_multiplier=3.0,
                baseline_version="v1.0",
            ),
        )
        assert isinstance(cb.evidence, RagEvidence)

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ContractSavingsCategoryBreakdown(
                category="local_routing",
                tier="direct",
                tokens_saved=100,
                cost_saved_usd=0.01,
                confidence=1.5,
                method="reference_pricing",
                evidence=LocalRoutingEvidence(
                    reference_model_id="x",
                    reference_cost_usd=0.1,
                    actual_model_id="y",
                    actual_cost_usd=0.01,
                    call_count=1,
                ),
            )
        with pytest.raises(ValidationError):
            ContractSavingsCategoryBreakdown(
                category="local_routing",
                tier="direct",
                tokens_saved=100,
                cost_saved_usd=0.01,
                confidence=-0.1,
                method="reference_pricing",
                evidence=LocalRoutingEvidence(
                    reference_model_id="x",
                    reference_cost_usd=0.1,
                    actual_model_id="y",
                    actual_cost_usd=0.01,
                    call_count=1,
                ),
            )


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------


def _routing_category(
    tokens: int = 5000, cost: float = 0.08, confidence: float = 0.95
) -> ContractSavingsCategoryBreakdown:
    return ContractSavingsCategoryBreakdown(
        category="local_routing",
        tier="direct",
        tokens_saved=tokens,
        cost_saved_usd=cost,
        confidence=confidence,
        method="reference_pricing",
        evidence=LocalRoutingEvidence(
            reference_model_id="claude-opus-4-20250514",
            reference_cost_usd=0.10,
            actual_model_id="qwen3-coder-30b",
            actual_cost_usd=0.002,
            call_count=5,
        ),
    )


def _validator_category(
    tokens: int = 15000, cost: float = 0.05, confidence: float = 0.7
) -> ContractSavingsCategoryBreakdown:
    return ContractSavingsCategoryBreakdown(
        category="validator_catches",
        tier="heuristic",
        tokens_saved=tokens,
        cost_saved_usd=cost,
        confidence=confidence,
        method="counted_catches",
        evidence=ValidatorCatchEvidence(
            catch_count=10,
            catches_by_severity={"error": 10},
            catches_by_type={"type_mismatch": 10},
            tokens_per_fix_cycle_weighted=1500,
            fix_cycle_baseline_version="v1.0",
        ),
    )


def _pattern_category(
    tokens: int = 1250, cost: float = 0.02, confidence: float = 0.6
) -> ContractSavingsCategoryBreakdown:
    return ContractSavingsCategoryBreakdown(
        category="pattern_injection",
        tier="heuristic",
        tokens_saved=tokens,
        cost_saved_usd=cost,
        confidence=confidence,
        method="historical_baseline",
        evidence=PatternInjectionEvidence(
            patterns_injected=3,
            tokens_injected=500,
            regen_multiplier=2.5,
        ),
    )


def _make_estimate(
    categories: list[ContractSavingsCategoryBreakdown] | None = None,
) -> ContractSavingsEstimate:
    if categories is None:
        categories = [_routing_category(), _validator_category(), _pattern_category()]

    direct_cats = [c for c in categories if c.tier == "direct"]
    heuristic_cats = [c for c in categories if c.tier == "heuristic"]

    direct_savings = sum(c.cost_saved_usd for c in direct_cats)
    direct_tokens = sum(c.tokens_saved for c in direct_cats)
    total_savings = sum(c.cost_saved_usd for c in categories)
    total_tokens = sum(c.tokens_saved for c in categories)

    direct_conf = direct_cats[0].confidence if direct_cats else 0.0

    heuristic_conf_avg = 0.0
    if heuristic_cats:
        total_cost = sum(c.cost_saved_usd for c in heuristic_cats)
        if total_cost > 0:
            heuristic_conf_avg = (
                sum(c.confidence * c.cost_saved_usd for c in heuristic_cats)
                / total_cost
            )

    return ContractSavingsEstimate(
        session_id="sess-001",
        correlation_id="corr-001",
        timestamp_iso="2026-03-19T12:00:00Z",
        actual_total_tokens=50000,
        actual_cost_usd=0.25,
        actual_model_id="qwen3-coder-30b",
        counterfactual_model_id="claude-opus-4-20250514",
        direct_savings_usd=direct_savings,
        direct_tokens_saved=direct_tokens,
        estimated_total_savings_usd=total_savings,
        estimated_total_tokens_saved=total_tokens,
        categories=categories,
        direct_confidence=direct_conf,
        heuristic_confidence_avg=heuristic_conf_avg,
        estimation_method="tiered_attribution",
        treatment_group="treatment",
    )


# ---------------------------------------------------------------------------
# ContractSavingsEstimate
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractSavingsEstimate:
    """Tests for ContractSavingsEstimate."""

    def test_create_minimal(self) -> None:
        est = _make_estimate()
        assert est.schema_version == "1.0"
        assert est.session_id == "sess-001"
        assert est.is_measured is False
        assert est.completeness_status == "complete"
        assert est.extensions == {}

    def test_frozen(self) -> None:
        est = _make_estimate()
        with pytest.raises(ValidationError):
            est.session_id = "changed"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractSavingsEstimate(
                session_id="s",
                correlation_id="c",
                timestamp_iso="t",
                actual_total_tokens=0,
                actual_cost_usd=0.0,
                actual_model_id="m",
                counterfactual_model_id="m2",
                direct_savings_usd=0.0,
                direct_tokens_saved=0,
                estimated_total_savings_usd=0.0,
                estimated_total_tokens_saved=0,
                categories=[],
                direct_confidence=0.0,
                heuristic_confidence_avg=0.0,
                estimation_method="x",
                treatment_group="control",
                bad="no",  # type: ignore[call-arg]
            )

    def test_direct_savings_equals_sum_of_direct_categories(self) -> None:
        routing = _routing_category(cost=0.08)
        validator = _validator_category(cost=0.05)
        pattern = _pattern_category(cost=0.02)
        est = _make_estimate([routing, validator, pattern])

        direct_sum = sum(c.cost_saved_usd for c in est.categories if c.tier == "direct")
        assert est.direct_savings_usd == pytest.approx(direct_sum)
        assert est.direct_savings_usd == pytest.approx(0.08)

    def test_estimated_total_savings_equals_sum_of_all_categories(self) -> None:
        routing = _routing_category(cost=0.08)
        validator = _validator_category(cost=0.05)
        pattern = _pattern_category(cost=0.02)
        est = _make_estimate([routing, validator, pattern])

        total_sum = sum(c.cost_saved_usd for c in est.categories)
        assert est.estimated_total_savings_usd == pytest.approx(total_sum)
        assert est.estimated_total_savings_usd == pytest.approx(0.15)

    def test_direct_confidence_reflects_tier_a(self) -> None:
        routing = _routing_category(confidence=0.95)
        validator = _validator_category(confidence=0.7)
        est = _make_estimate([routing, validator])
        assert est.direct_confidence == pytest.approx(0.95)

    def test_heuristic_confidence_avg_cost_weighted(self) -> None:
        validator = _validator_category(cost=0.05, confidence=0.7)
        pattern = _pattern_category(cost=0.02, confidence=0.6)
        est = _make_estimate([_routing_category(), validator, pattern])

        total_heuristic_cost = 0.05 + 0.02
        expected_avg = (0.7 * 0.05 + 0.6 * 0.02) / total_heuristic_cost
        assert est.heuristic_confidence_avg == pytest.approx(expected_avg)

    def test_confidence_bounds_direct(self) -> None:
        est = _make_estimate()
        assert 0.0 <= est.direct_confidence <= 1.0

    def test_confidence_bounds_heuristic(self) -> None:
        est = _make_estimate()
        assert 0.0 <= est.heuristic_confidence_avg <= 1.0

    def test_completeness_phase_limited(self) -> None:
        est = ContractSavingsEstimate(
            session_id="s",
            correlation_id="c",
            timestamp_iso="t",
            actual_total_tokens=1000,
            actual_cost_usd=0.01,
            actual_model_id="m",
            counterfactual_model_id="m2",
            direct_savings_usd=0.0,
            direct_tokens_saved=0,
            estimated_total_savings_usd=0.0,
            estimated_total_tokens_saved=0,
            categories=[],
            direct_confidence=0.0,
            heuristic_confidence_avg=0.0,
            estimation_method="tiered_attribution",
            treatment_group="treatment",
            completeness_status="phase_limited",
        )
        assert est.completeness_status == "phase_limited"

    def test_completeness_partial(self) -> None:
        est = ContractSavingsEstimate(
            session_id="s",
            correlation_id="c",
            timestamp_iso="t",
            actual_total_tokens=1000,
            actual_cost_usd=0.01,
            actual_model_id="m",
            counterfactual_model_id="m2",
            direct_savings_usd=0.08,
            direct_tokens_saved=5000,
            estimated_total_savings_usd=0.08,
            estimated_total_tokens_saved=5000,
            categories=[_routing_category()],
            direct_confidence=0.95,
            heuristic_confidence_avg=0.0,
            estimation_method="tiered_attribution",
            treatment_group="treatment",
            completeness_status="partial",
        )
        assert est.completeness_status == "partial"

    def test_json_round_trip(self) -> None:
        est = _make_estimate()
        j = est.model_dump_json()
        est2 = ContractSavingsEstimate.model_validate_json(j)
        assert est == est2

    def test_dict_round_trip(self) -> None:
        est = _make_estimate()
        d = est.model_dump()
        assert isinstance(d, dict)
        est2 = ContractSavingsEstimate.model_validate(d)
        assert est == est2

    def test_dict_via_json_str(self) -> None:
        est = _make_estimate()
        j_str = est.model_dump_json()
        d = json.loads(j_str)
        est2 = ContractSavingsEstimate.model_validate(d)
        assert est == est2

    def test_extensions_field(self) -> None:
        est = ContractSavingsEstimate(
            session_id="s",
            correlation_id="c",
            timestamp_iso="t",
            actual_total_tokens=1000,
            actual_cost_usd=0.01,
            actual_model_id="m",
            counterfactual_model_id="m2",
            direct_savings_usd=0.0,
            direct_tokens_saved=0,
            estimated_total_savings_usd=0.0,
            estimated_total_tokens_saved=0,
            categories=[],
            direct_confidence=0.0,
            heuristic_confidence_avg=0.0,
            estimation_method="x",
            treatment_group="control",
            extensions={"custom_key": "custom_value"},
        )
        assert est.extensions == {"custom_key": "custom_value"}

    def test_is_measured_flag(self) -> None:
        est = ContractSavingsEstimate(
            session_id="s",
            correlation_id="c",
            timestamp_iso="t",
            actual_total_tokens=1000,
            actual_cost_usd=0.01,
            actual_model_id="m",
            counterfactual_model_id="m2",
            direct_savings_usd=0.0,
            direct_tokens_saved=0,
            estimated_total_savings_usd=0.0,
            estimated_total_tokens_saved=0,
            categories=[],
            direct_confidence=0.0,
            heuristic_confidence_avg=0.0,
            estimation_method="x",
            treatment_group="control",
            is_measured=True,
            measurement_basis="a_b_test",
            baseline_session_id="baseline-001",
        )
        assert est.is_measured is True
        assert est.measurement_basis == "a_b_test"


# ---------------------------------------------------------------------------
# Module import test
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSavingsEstimateModuleImports:
    """Tests that savings estimate models are importable from measurement package."""

    def test_import_from_measurement_init(self) -> None:
        from omnibase_spi.contracts.measurement import (
            ContractSavingsCategoryBreakdown,
            ContractSavingsEstimate,
            LocalRoutingEvidence,
        )

        assert ContractSavingsEstimate is not None
        assert ContractSavingsCategoryBreakdown is not None
        assert LocalRoutingEvidence is not None
