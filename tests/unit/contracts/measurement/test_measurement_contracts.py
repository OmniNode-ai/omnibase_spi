"""Tests for all measurement contracts.

Covers:
- Enum stability (member count and values)
- Frozen immutability
- extra="forbid" rejects unknown fields
- extensions field present on all contracts
- schema_version present on all contracts
- JSON round-trip serialization
- Model validators (skip_reason_code invariant)
- ContractMeasurementContext baseline key derivation
- ContractAggregatedRun overall_result semantics
- ContractPromotionGate delta_pct=None when baseline=0
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.measurement.contract_aggregated_run import (
    ContractAggregatedRun,
)
from omnibase_spi.contracts.measurement.contract_measured_attribution import (
    ContractMeasuredAttribution,
)
from omnibase_spi.contracts.measurement.contract_measurement_context import (
    ContractMeasurementContext,
    derive_baseline_key,
)
from omnibase_spi.contracts.measurement.contract_measurement_event import (
    ContractMeasurementEvent,
)
from omnibase_spi.contracts.measurement.contract_phase_metrics import (
    ContractArtifactPointerMeasurement,
    ContractCostMetrics,
    ContractDurationMetrics,
    ContractOutcomeMetrics,
    ContractPhaseMetrics,
    ContractTestMetrics,
)
from omnibase_spi.contracts.measurement.contract_producer import ContractProducer
from omnibase_spi.contracts.measurement.contract_promotion_gate import (
    ContractDimensionEvidence,
    ContractPromotionGate,
)
from omnibase_spi.contracts.measurement.enum_measurement_check import MeasurementCheck
from omnibase_spi.contracts.measurement.enum_pipeline_phase import (
    ContractEnumPipelinePhase,
)
from omnibase_spi.contracts.measurement.enum_result_classification import (
    ContractEnumResultClassification,
)


# ---------------------------------------------------------------------------
# Enum stability tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractEnumPipelinePhase:
    """Tests for ContractEnumPipelinePhase enum stability."""

    def test_has_five_members(self) -> None:
        assert len(ContractEnumPipelinePhase) == 5

    def test_member_values(self) -> None:
        assert ContractEnumPipelinePhase.PLAN == "plan"
        assert ContractEnumPipelinePhase.IMPLEMENT == "implement"
        assert ContractEnumPipelinePhase.VERIFY == "verify"
        assert ContractEnumPipelinePhase.REVIEW == "review"
        assert ContractEnumPipelinePhase.RELEASE == "release"

    def test_is_str_enum(self) -> None:
        for member in ContractEnumPipelinePhase:
            assert isinstance(member, str)


@pytest.mark.unit
class TestContractEnumResultClassification:
    """Tests for ContractEnumResultClassification enum stability."""

    def test_has_five_members(self) -> None:
        assert len(ContractEnumResultClassification) == 5

    def test_member_values(self) -> None:
        assert ContractEnumResultClassification.SUCCESS == "success"
        assert ContractEnumResultClassification.FAILURE == "failure"
        assert ContractEnumResultClassification.PARTIAL == "partial"
        assert ContractEnumResultClassification.SKIPPED == "skipped"
        assert ContractEnumResultClassification.ERROR == "error"

    def test_is_str_enum(self) -> None:
        for member in ContractEnumResultClassification:
            assert isinstance(member, str)


@pytest.mark.unit
class TestMeasurementCheck:
    """Tests for MeasurementCheck enum stability."""

    def test_has_six_members(self) -> None:
        assert len(MeasurementCheck) == 6

    def test_member_values(self) -> None:
        assert MeasurementCheck.CHECK_MEAS_001 == "CHECK-MEAS-001"
        assert MeasurementCheck.CHECK_MEAS_002 == "CHECK-MEAS-002"
        assert MeasurementCheck.CHECK_MEAS_003 == "CHECK-MEAS-003"
        assert MeasurementCheck.CHECK_MEAS_004 == "CHECK-MEAS-004"
        assert MeasurementCheck.CHECK_MEAS_005 == "CHECK-MEAS-005"
        assert MeasurementCheck.CHECK_MEAS_006 == "CHECK-MEAS-006"

    def test_all_start_with_check_prefix(self) -> None:
        for check in MeasurementCheck:
            assert check.value.startswith("CHECK-MEAS-")

    def test_is_str_enum(self) -> None:
        for member in MeasurementCheck:
            assert isinstance(member, str)


# ---------------------------------------------------------------------------
# ContractMeasurementContext
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractMeasurementContext:
    """Tests for ContractMeasurementContext."""

    def test_create_minimal(self) -> None:
        ctx = ContractMeasurementContext(ticket_id="OMN-2024")
        assert ctx.ticket_id == "OMN-2024"
        assert ctx.schema_version == "1.0"
        assert ctx.repo_id == ""
        assert ctx.toolchain == ""
        assert ctx.strictness == "default"
        assert ctx.scenario_id == ""
        assert ctx.pattern_id == ""
        assert ctx.extensions == {}

    def test_create_full(self) -> None:
        ctx = ContractMeasurementContext(
            ticket_id="OMN-2024",
            repo_id="omnibase_spi",
            toolchain="poetry",
            strictness="strict",
            scenario_id="sc-001",
            pattern_id="pat-001",
            extensions={"env": "ci"},
        )
        assert ctx.repo_id == "omnibase_spi"
        assert ctx.toolchain == "poetry"
        assert ctx.strictness == "strict"
        assert ctx.extensions == {"env": "ci"}

    def test_frozen(self) -> None:
        ctx = ContractMeasurementContext(ticket_id="OMN-2024")
        with pytest.raises(ValidationError):
            ctx.ticket_id = "changed"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractMeasurementContext(
                ticket_id="OMN-2024",
                unknown_field="rejected",  # type: ignore[call-arg]
            )

    def test_json_round_trip(self) -> None:
        ctx = ContractMeasurementContext(
            ticket_id="OMN-2024",
            repo_id="omnibase_spi",
            toolchain="poetry",
            strictness="strict",
        )
        j = ctx.model_dump_json()
        ctx2 = ContractMeasurementContext.model_validate_json(j)
        assert ctx == ctx2

    def test_baseline_key_deterministic(self) -> None:
        ctx = ContractMeasurementContext(
            ticket_id="OMN-2024",
            repo_id="omnibase_spi",
            toolchain="poetry",
        )
        key1 = derive_baseline_key(ctx)
        key2 = derive_baseline_key(ctx)
        assert key1 == key2
        assert len(key1) == 64  # SHA-256 hex digest

    def test_baseline_key_differs_for_different_inputs(self) -> None:
        ctx_a = ContractMeasurementContext(ticket_id="OMN-2024")
        ctx_b = ContractMeasurementContext(ticket_id="OMN-2025")
        assert derive_baseline_key(ctx_a) != derive_baseline_key(ctx_b)


# ---------------------------------------------------------------------------
# ContractProducer
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractProducer:
    """Tests for ContractProducer."""

    def test_create_minimal(self) -> None:
        p = ContractProducer(name="ticket-pipeline")
        assert p.name == "ticket-pipeline"
        assert p.schema_version == "1.0"
        assert p.version == ""
        assert p.instance_id == ""
        assert p.extensions == {}

    def test_create_full(self) -> None:
        p = ContractProducer(
            name="ticket-pipeline",
            version="1.2.0",
            instance_id="inst-abc",
            extensions={"host": "ci-runner-1"},
        )
        assert p.version == "1.2.0"
        assert p.instance_id == "inst-abc"

    def test_frozen(self) -> None:
        p = ContractProducer(name="x")
        with pytest.raises(ValidationError):
            p.name = "y"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractProducer(
                name="x",
                bogus="rejected",  # type: ignore[call-arg]
            )

    def test_json_round_trip(self) -> None:
        p = ContractProducer(name="pytest", version="8.4.2")
        j = p.model_dump_json()
        p2 = ContractProducer.model_validate_json(j)
        assert p == p2


# ---------------------------------------------------------------------------
# Phase metrics sub-contracts
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractDurationMetrics:
    """Tests for ContractDurationMetrics."""

    def test_create(self) -> None:
        dm = ContractDurationMetrics(wall_clock_ms=1500.0, cpu_ms=1200.0)
        assert dm.wall_clock_ms == 1500.0
        assert dm.cpu_ms == 1200.0
        assert dm.queue_ms is None

    def test_frozen(self) -> None:
        dm = ContractDurationMetrics(wall_clock_ms=100.0)
        with pytest.raises(ValidationError):
            dm.wall_clock_ms = 200.0  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractDurationMetrics(
                wall_clock_ms=100.0,
                extra_field="no",  # type: ignore[call-arg]
            )


@pytest.mark.unit
class TestContractCostMetrics:
    """Tests for ContractCostMetrics."""

    def test_create(self) -> None:
        cm = ContractCostMetrics(
            llm_input_tokens=500, llm_output_tokens=200, llm_total_tokens=700
        )
        assert cm.llm_total_tokens == 700
        assert cm.estimated_cost_usd is None

    def test_defaults(self) -> None:
        cm = ContractCostMetrics()
        assert cm.llm_input_tokens == 0
        assert cm.llm_output_tokens == 0
        assert cm.llm_total_tokens == 0

    def test_negative_tokens_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ContractCostMetrics(llm_input_tokens=-1)

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractCostMetrics(nope="rejected")  # type: ignore[call-arg]


@pytest.mark.unit
class TestContractOutcomeMetrics:
    """Tests for ContractOutcomeMetrics."""

    def test_create_success(self) -> None:
        om = ContractOutcomeMetrics(
            result_classification=ContractEnumResultClassification.SUCCESS,
        )
        assert om.result_classification == ContractEnumResultClassification.SUCCESS
        assert om.error_messages == []
        assert om.skip_reason_code == ""

    def test_skipped_requires_skip_reason_code(self) -> None:
        with pytest.raises(ValidationError, match="skip_reason_code"):
            ContractOutcomeMetrics(
                result_classification=ContractEnumResultClassification.SKIPPED,
            )

    def test_skipped_with_skip_reason_code(self) -> None:
        om = ContractOutcomeMetrics(
            result_classification=ContractEnumResultClassification.SKIPPED,
            skip_reason="Not applicable for this repo",
            skip_reason_code="NOT_APPLICABLE",
        )
        assert om.skip_reason_code == "NOT_APPLICABLE"

    def test_failure_with_errors(self) -> None:
        om = ContractOutcomeMetrics(
            result_classification=ContractEnumResultClassification.FAILURE,
            error_messages=["Test suite failed"],
            error_codes=["TEST-FAIL-001"],
            failed_tests=["test_foo", "test_bar"],
        )
        assert len(om.error_messages) == 1
        assert len(om.failed_tests) == 2

    def test_frozen(self) -> None:
        om = ContractOutcomeMetrics(
            result_classification=ContractEnumResultClassification.SUCCESS,
        )
        with pytest.raises(ValidationError):
            om.result_classification = ContractEnumResultClassification.FAILURE  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractOutcomeMetrics(
                result_classification=ContractEnumResultClassification.SUCCESS,
                nope="rejected",  # type: ignore[call-arg]
            )


@pytest.mark.unit
class TestContractTestMetrics:
    """Tests for ContractTestMetrics."""

    def test_create(self) -> None:
        tm = ContractTestMetrics(
            total_tests=100,
            passed_tests=95,
            failed_tests=3,
            skipped_tests=2,
            error_tests=0,
            pass_rate=0.95,
        )
        assert tm.total_tests == 100
        assert tm.pass_rate == 0.95

    def test_pass_rate_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ContractTestMetrics(pass_rate=1.5)  # > 1.0
        with pytest.raises(ValidationError):
            ContractTestMetrics(pass_rate=-0.1)  # < 0.0

    def test_negative_counts_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ContractTestMetrics(total_tests=-1)

    def test_defaults(self) -> None:
        tm = ContractTestMetrics()
        assert tm.total_tests == 0
        assert tm.pass_rate is None


@pytest.mark.unit
class TestContractArtifactPointerMeasurement:
    """Tests for ContractArtifactPointerMeasurement."""

    def test_create(self) -> None:
        ap = ContractArtifactPointerMeasurement(
            artifact_type="pr",
            name="PR #42",
            uri="https://github.com/org/repo/pull/42",
        )
        assert ap.artifact_type == "pr"
        assert ap.name == "PR #42"
        assert ap.checksum == ""

    def test_frozen(self) -> None:
        ap = ContractArtifactPointerMeasurement(artifact_type="file")
        with pytest.raises(ValidationError):
            ap.artifact_type = "commit"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractArtifactPointerMeasurement(
                artifact_type="x",
                bad="no",  # type: ignore[call-arg]
            )


# ---------------------------------------------------------------------------
# ContractPhaseMetrics (primary measurement unit)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractPhaseMetrics:
    """Tests for ContractPhaseMetrics."""

    def test_create_minimal(self) -> None:
        pm = ContractPhaseMetrics(
            run_id="run-001",
            phase=ContractEnumPipelinePhase.IMPLEMENT,
        )
        assert pm.run_id == "run-001"
        assert pm.phase == ContractEnumPipelinePhase.IMPLEMENT
        assert pm.attempt == 1
        assert pm.context is None
        assert pm.producer is None
        assert pm.duration is None
        assert pm.cost is None
        assert pm.outcome is None
        assert pm.tests is None
        assert pm.artifact_pointers == []
        assert pm.extensions == {}

    def test_create_full(self) -> None:
        ctx = ContractMeasurementContext(ticket_id="OMN-2024")
        producer = ContractProducer(name="ticket-pipeline")
        duration = ContractDurationMetrics(wall_clock_ms=5000.0)
        cost = ContractCostMetrics(llm_total_tokens=1000)
        outcome = ContractOutcomeMetrics(
            result_classification=ContractEnumResultClassification.SUCCESS,
        )
        tests = ContractTestMetrics(total_tests=50, passed_tests=50, pass_rate=1.0)
        artifact = ContractArtifactPointerMeasurement(
            artifact_type="commit", uri="abc123"
        )

        pm = ContractPhaseMetrics(
            run_id="run-001",
            phase=ContractEnumPipelinePhase.VERIFY,
            phase_id="phase-verify-1",
            attempt=2,
            context=ctx,
            producer=producer,
            duration=duration,
            cost=cost,
            outcome=outcome,
            tests=tests,
            artifact_pointers=[artifact],
            extensions={"ci": True},
        )
        assert pm.attempt == 2
        assert pm.context is not None
        assert pm.context.ticket_id == "OMN-2024"
        assert len(pm.artifact_pointers) == 1
        assert pm.extensions == {"ci": True}

    def test_frozen(self) -> None:
        pm = ContractPhaseMetrics(
            run_id="run-001",
            phase=ContractEnumPipelinePhase.PLAN,
        )
        with pytest.raises(ValidationError):
            pm.run_id = "changed"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractPhaseMetrics(
                run_id="run-001",
                phase=ContractEnumPipelinePhase.PLAN,
                nope="no",  # type: ignore[call-arg]
            )

    def test_attempt_ge_1(self) -> None:
        with pytest.raises(ValidationError):
            ContractPhaseMetrics(
                run_id="run-001",
                phase=ContractEnumPipelinePhase.PLAN,
                attempt=0,
            )

    def test_json_round_trip(self) -> None:
        pm = ContractPhaseMetrics(
            run_id="run-001",
            phase=ContractEnumPipelinePhase.IMPLEMENT,
            context=ContractMeasurementContext(ticket_id="OMN-2024"),
            producer=ContractProducer(name="pipeline"),
            duration=ContractDurationMetrics(wall_clock_ms=1000.0),
            cost=ContractCostMetrics(llm_total_tokens=500),
            outcome=ContractOutcomeMetrics(
                result_classification=ContractEnumResultClassification.SUCCESS,
            ),
            tests=ContractTestMetrics(total_tests=10, passed_tests=10, pass_rate=1.0),
        )
        j = pm.model_dump_json()
        pm2 = ContractPhaseMetrics.model_validate_json(j)
        assert pm == pm2


# ---------------------------------------------------------------------------
# ContractMeasurementEvent
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractMeasurementEvent:
    """Tests for ContractMeasurementEvent."""

    def test_create(self) -> None:
        payload = ContractPhaseMetrics(
            run_id="run-001",
            phase=ContractEnumPipelinePhase.IMPLEMENT,
        )
        evt = ContractMeasurementEvent(
            event_id="evt-001",
            payload=payload,
        )
        assert evt.event_id == "evt-001"
        assert evt.event_type == "phase_completed"
        assert evt.payload.run_id == "run-001"

    def test_frozen(self) -> None:
        payload = ContractPhaseMetrics(
            run_id="run-001",
            phase=ContractEnumPipelinePhase.PLAN,
        )
        evt = ContractMeasurementEvent(event_id="e", payload=payload)
        with pytest.raises(ValidationError):
            evt.event_id = "changed"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        payload = ContractPhaseMetrics(
            run_id="run-001",
            phase=ContractEnumPipelinePhase.PLAN,
        )
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractMeasurementEvent(
                event_id="e",
                payload=payload,
                nope="no",  # type: ignore[call-arg]
            )

    def test_json_round_trip(self) -> None:
        payload = ContractPhaseMetrics(
            run_id="run-001",
            phase=ContractEnumPipelinePhase.REVIEW,
        )
        evt = ContractMeasurementEvent(
            event_id="evt-002",
            event_type="phase_started",
            timestamp_iso="2026-02-08T12:00:00Z",
            payload=payload,
        )
        j = evt.model_dump_json()
        evt2 = ContractMeasurementEvent.model_validate_json(j)
        assert evt == evt2


# ---------------------------------------------------------------------------
# ContractAggregatedRun
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractAggregatedRun:
    """Tests for ContractAggregatedRun."""

    def test_create_success(self) -> None:
        run = ContractAggregatedRun(
            run_id="run-001",
            overall_result="success",
            mandatory_phases_total=3,
            mandatory_phases_succeeded=3,
        )
        assert run.overall_result == "success"
        assert run.mandatory_phases_total == 3

    def test_create_partial(self) -> None:
        run = ContractAggregatedRun(
            run_id="run-002",
            overall_result="partial",
            mandatory_phases_total=3,
            mandatory_phases_succeeded=2,
        )
        assert run.overall_result == "partial"

    def test_create_failure(self) -> None:
        run = ContractAggregatedRun(
            run_id="run-003",
            overall_result="failure",
        )
        assert run.overall_result == "failure"

    def test_negative_mandatory_phases_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ContractAggregatedRun(
                run_id="run-001",
                overall_result="success",
                mandatory_phases_total=-1,
            )

    def test_invalid_overall_result(self) -> None:
        with pytest.raises(ValidationError):
            ContractAggregatedRun(
                run_id="run-004",
                overall_result="unknown",  # type: ignore[arg-type]
            )

    def test_with_phase_metrics(self) -> None:
        phases = [
            ContractPhaseMetrics(
                run_id="run-001",
                phase=ContractEnumPipelinePhase.IMPLEMENT,
            ),
            ContractPhaseMetrics(
                run_id="run-001",
                phase=ContractEnumPipelinePhase.VERIFY,
            ),
        ]
        run = ContractAggregatedRun(
            run_id="run-001",
            overall_result="success",
            phase_metrics=phases,
            total_duration_ms=10000.0,
            total_cost_usd=0.05,
        )
        assert len(run.phase_metrics) == 2
        assert run.total_duration_ms == 10000.0

    def test_frozen(self) -> None:
        run = ContractAggregatedRun(run_id="run-001", overall_result="success")
        with pytest.raises(ValidationError):
            run.run_id = "changed"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractAggregatedRun(
                run_id="run-001",
                overall_result="success",
                nope="no",  # type: ignore[call-arg]
            )

    def test_json_round_trip(self) -> None:
        run = ContractAggregatedRun(
            run_id="run-001",
            overall_result="success",
            context=ContractMeasurementContext(ticket_id="OMN-2024"),
            total_duration_ms=5000.0,
        )
        j = run.model_dump_json()
        run2 = ContractAggregatedRun.model_validate_json(j)
        assert run == run2


# ---------------------------------------------------------------------------
# ContractPromotionGate and ContractDimensionEvidence
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractDimensionEvidence:
    """Tests for ContractDimensionEvidence."""

    def test_create(self) -> None:
        de = ContractDimensionEvidence(
            dimension="test_pass_rate",
            baseline_value=0.90,
            current_value=0.95,
            delta_pct=5.56,
            threshold=0.90,
            sufficient=True,
        )
        assert de.dimension == "test_pass_rate"
        assert de.sufficient is True

    def test_delta_pct_none_when_baseline_zero(self) -> None:
        de = ContractDimensionEvidence(
            dimension="new_metric",
            baseline_value=0.0,
            current_value=100.0,
            delta_pct=None,
            sufficient=True,
        )
        assert de.delta_pct is None

    def test_frozen(self) -> None:
        de = ContractDimensionEvidence(dimension="x")
        with pytest.raises(ValidationError):
            de.dimension = "y"  # type: ignore[misc]

    def test_delta_pct_must_be_none_when_baseline_zero(self) -> None:
        """delta_pct must be None when baseline_value is 0."""
        with pytest.raises(ValidationError, match="delta_pct"):
            ContractDimensionEvidence(
                dimension="x",
                baseline_value=0.0,
                current_value=10.0,
                delta_pct=100.0,  # Should fail: baseline is 0
            )

    def test_delta_pct_allowed_when_baseline_nonzero(self) -> None:
        """delta_pct can be set when baseline_value is non-zero."""
        de = ContractDimensionEvidence(
            dimension="x",
            baseline_value=50.0,
            current_value=75.0,
            delta_pct=50.0,
        )
        assert de.delta_pct == 50.0

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractDimensionEvidence(
                dimension="x",
                bad="no",  # type: ignore[call-arg]
            )


@pytest.mark.unit
class TestContractPromotionGate:
    """Tests for ContractPromotionGate."""

    def test_create_pass(self) -> None:
        gate = ContractPromotionGate(
            run_id="run-001",
            gate_result="pass",
            sufficient_count=3,
            total_count=3,
        )
        assert gate.gate_result == "pass"
        assert gate.baseline_key == ""

    def test_create_with_context_derived_key(self) -> None:
        ctx = ContractMeasurementContext(
            ticket_id="OMN-2024", repo_id="omnibase_spi"
        )
        gate = ContractPromotionGate(
            run_id="run-001",
            context=ctx,
            baseline_key=derive_baseline_key(ctx),
            gate_result="pass",
        )
        assert gate.baseline_key == derive_baseline_key(ctx)
        assert len(gate.baseline_key) == 64

    def test_create_fail(self) -> None:
        gate = ContractPromotionGate(
            run_id="run-001",
            gate_result="fail",
            dimensions=[
                ContractDimensionEvidence(
                    dimension="cost",
                    baseline_value=100.0,
                    current_value=150.0,
                    delta_pct=50.0,
                    threshold=10.0,
                    sufficient=False,
                ),
            ],
            required_dimensions=["cost"],
        )
        assert gate.gate_result == "fail"
        assert len(gate.dimensions) == 1
        assert gate.dimensions[0].sufficient is False

    def test_create_insufficient_evidence(self) -> None:
        gate = ContractPromotionGate(
            run_id="run-001",
            gate_result="insufficient_evidence",
        )
        assert gate.gate_result == "insufficient_evidence"

    def test_negative_counts_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ContractPromotionGate(
                run_id="run-001",
                gate_result="pass",
                sufficient_count=-1,
            )

    def test_invalid_gate_result(self) -> None:
        with pytest.raises(ValidationError):
            ContractPromotionGate(
                run_id="run-001",
                gate_result="maybe",  # type: ignore[arg-type]
            )

    def test_frozen(self) -> None:
        gate = ContractPromotionGate(run_id="run-001", gate_result="pass")
        with pytest.raises(ValidationError):
            gate.run_id = "changed"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractPromotionGate(
                run_id="run-001",
                gate_result="pass",
                nope="no",  # type: ignore[call-arg]
            )

    def test_json_round_trip(self) -> None:
        gate = ContractPromotionGate(
            run_id="run-001",
            gate_result="pass",
            dimensions=[
                ContractDimensionEvidence(
                    dimension="test_pass_rate",
                    baseline_value=0.90,
                    current_value=0.95,
                    delta_pct=5.56,
                    sufficient=True,
                ),
            ],
            sufficient_count=1,
            total_count=1,
        )
        j = gate.model_dump_json()
        gate2 = ContractPromotionGate.model_validate_json(j)
        assert gate == gate2


# ---------------------------------------------------------------------------
# ContractMeasuredAttribution
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractMeasuredAttribution:
    """Tests for ContractMeasuredAttribution."""

    def test_create_minimal(self) -> None:
        attr = ContractMeasuredAttribution(attribution_id="attr-001")
        assert attr.attribution_id == "attr-001"
        assert attr.schema_version == "1.0"
        assert attr.context is None
        assert attr.aggregated_run is None
        assert attr.promotion_gate is None
        assert attr.verdict == ""
        assert attr.promoted is False

    def test_create_full(self) -> None:
        ctx = ContractMeasurementContext(ticket_id="OMN-2024")
        run = ContractAggregatedRun(run_id="run-001", overall_result="success")
        gate = ContractPromotionGate(run_id="run-001", gate_result="pass")

        attr = ContractMeasuredAttribution(
            attribution_id="attr-001",
            context=ctx,
            proposed_by="agent-x",
            proposed_at_iso="2026-02-08T12:00:00Z",
            aggregated_run=run,
            promotion_gate=gate,
            verdict="PASS",
            promoted=True,
            promoted_at_iso="2026-02-08T13:00:00Z",
            promoted_to="production",
        )
        assert attr.verdict == "PASS"
        assert attr.promoted is True
        assert attr.promoted_to == "production"

    def test_invalid_verdict(self) -> None:
        with pytest.raises(ValidationError):
            ContractMeasuredAttribution(
                attribution_id="attr-001",
                verdict="MAYBE",  # type: ignore[arg-type]
            )

    def test_frozen(self) -> None:
        attr = ContractMeasuredAttribution(attribution_id="attr-001")
        with pytest.raises(ValidationError):
            attr.attribution_id = "changed"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractMeasuredAttribution(
                attribution_id="attr-001",
                nope="no",  # type: ignore[call-arg]
            )

    def test_json_round_trip(self) -> None:
        attr = ContractMeasuredAttribution(
            attribution_id="attr-001",
            context=ContractMeasurementContext(ticket_id="OMN-2024"),
            verdict="PASS",
            promoted=True,
        )
        j = attr.model_dump_json()
        attr2 = ContractMeasuredAttribution.model_validate_json(j)
        assert attr == attr2


# ---------------------------------------------------------------------------
# ContractCheckResult domain extension
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractCheckResultMeasurementDomain:
    """Tests that ContractCheckResult now accepts 'measurement' domain."""

    def test_measurement_domain_accepted(self) -> None:
        from omnibase_spi.contracts.shared.contract_check_result import (
            ContractCheckResult,
        )

        cr = ContractCheckResult(
            check_id="CHECK-MEAS-001",
            domain="measurement",
            status="pass",
        )
        assert cr.domain == "measurement"

    def test_existing_domains_still_work(self) -> None:
        from omnibase_spi.contracts.shared.contract_check_result import (
            ContractCheckResult,
        )

        for domain in ("rrh", "validation", "governance"):
            cr = ContractCheckResult(
                check_id="X",
                domain=domain,  # type: ignore[arg-type]
                status="pass",
            )
            assert cr.domain == domain


# ---------------------------------------------------------------------------
# Module-level import test
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMeasurementModuleImports:
    """Tests that all contracts are importable from the measurement package."""

    def test_import_from_measurement_init(self) -> None:
        from omnibase_spi.contracts.measurement import (
            ContractAggregatedRun,
            ContractArtifactPointerMeasurement,
            ContractCostMetrics,
            ContractDimensionEvidence,
            ContractDurationMetrics,
            ContractEnumPipelinePhase,
            ContractEnumResultClassification,
            ContractMeasuredAttribution,
            ContractMeasurementContext,
            ContractMeasurementEvent,
            ContractOutcomeMetrics,
            ContractPhaseMetrics,
            ContractProducer,
            ContractPromotionGate,
            ContractTestMetrics,
            MeasurementCheck,
        )

        # Verify they are the correct types
        assert ContractEnumPipelinePhase.PLAN == "plan"
        assert MeasurementCheck.CHECK_MEAS_001 == "CHECK-MEAS-001"

    def test_import_from_contracts_init(self) -> None:
        from omnibase_spi.contracts import (
            ContractAggregatedRun,
            ContractEnumPipelinePhase,
            ContractMeasurementContext,
            ContractPhaseMetrics,
            ContractProducer,
            ContractPromotionGate,
            MeasurementCheck,
        )

        assert ContractEnumPipelinePhase.IMPLEMENT == "implement"
        assert MeasurementCheck.CHECK_MEAS_006 == "CHECK-MEAS-006"


# ---------------------------------------------------------------------------
# Dict / JSON round-trip for raw dicts
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDictRoundTrip:
    """Test model_dump / model_validate round-trips via plain dicts."""

    def test_context_dict_round_trip(self) -> None:
        ctx = ContractMeasurementContext(
            ticket_id="OMN-2024", repo_id="omnibase_spi"
        )
        d = ctx.model_dump()
        assert isinstance(d, dict)
        ctx2 = ContractMeasurementContext.model_validate(d)
        assert ctx == ctx2

    def test_producer_dict_round_trip(self) -> None:
        p = ContractProducer(name="pytest", version="8.4.2")
        d = p.model_dump()
        p2 = ContractProducer.model_validate(d)
        assert p == p2

    def test_phase_metrics_dict_via_json_str(self) -> None:
        """Ensure the JSON string can be parsed back to dict then validated."""
        pm = ContractPhaseMetrics(
            run_id="run-001",
            phase=ContractEnumPipelinePhase.IMPLEMENT,
            context=ContractMeasurementContext(ticket_id="OMN-2024"),
        )
        j_str = pm.model_dump_json()
        d = json.loads(j_str)
        pm2 = ContractPhaseMetrics.model_validate(d)
        assert pm == pm2
