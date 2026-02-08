"""Tests for all validation contracts."""

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.shared.contract_check_result import ContractCheckResult
from omnibase_spi.contracts.shared.contract_verdict import ContractVerdict
from omnibase_spi.contracts.validation.contract_attribution_record import (
    ContractAttributionRecord,
)
from omnibase_spi.contracts.validation.contract_pattern_candidate import (
    ContractPatternCandidate,
)
from omnibase_spi.contracts.validation.contract_validation_plan import (
    ContractValidationPlan,
)
from omnibase_spi.contracts.validation.contract_validation_result import (
    ContractValidationResult,
)
from omnibase_spi.contracts.validation.contract_validation_run import (
    ContractValidationRun,
)
from omnibase_spi.contracts.validation.contract_validation_verdict import (
    ContractValidationVerdict,
)
from omnibase_spi.contracts.validation.enum_validation_check import ValidationCheck


@pytest.mark.unit
class TestContractPatternCandidate:
    """Tests for ContractPatternCandidate."""

    def test_create(self) -> None:
        pc = ContractPatternCandidate(
            pattern_id="pat-001",
            source="agent",
            pattern_type="code",
            content="def hello(): ...",
            language="python",
        )
        assert pc.pattern_id == "pat-001"
        assert pc.schema_version == "1.0"

    def test_frozen(self) -> None:
        pc = ContractPatternCandidate(pattern_id="x")
        with pytest.raises(ValidationError):
            pc.pattern_id = "y"  # type: ignore[misc]

    def test_forward_compat(self) -> None:
        pc = ContractPatternCandidate.model_validate(
            {"pattern_id": "x", "new_field": 42}
        )
        assert pc.model_extra is not None
        assert pc.model_extra["new_field"] == 42


@pytest.mark.unit
class TestContractValidationPlan:
    """Tests for ContractValidationPlan."""

    def test_create(self) -> None:
        plan = ContractValidationPlan(
            plan_id="plan-001",
            check_ids=["CHECK-PY-001", "CHECK-TEST-001"],
            pattern_id="pat-001",
        )
        assert plan.plan_id == "plan-001"
        assert len(plan.check_ids) == 2

    def test_with_parameters(self) -> None:
        plan = ContractValidationPlan(
            plan_id="plan-002",
            check_ids=["CHECK-TEST-003"],
            parameters={"CHECK-TEST-003": {"threshold": 80}},
        )
        assert plan.parameters["CHECK-TEST-003"]["threshold"] == 80


@pytest.mark.unit
class TestContractValidationRun:
    """Tests for ContractValidationRun."""

    def test_create(self) -> None:
        run = ContractValidationRun(
            run_id="run-001",
            plan_id="plan-001",
            status="completed",
            duration_ms=1500.0,
        )
        assert run.run_id == "run-001"
        assert run.status == "completed"

    def test_default_status(self) -> None:
        run = ContractValidationRun(run_id="run-002")
        assert run.status == "pending"


@pytest.mark.unit
class TestContractValidationResult:
    """Tests for ContractValidationResult."""

    def test_create_with_checks(self) -> None:
        checks = [
            ContractCheckResult(
                check_id="CHECK-PY-001", domain="validation", status="pass"
            ),
            ContractCheckResult(
                check_id="CHECK-TEST-001", domain="validation", status="fail"
            ),
        ]
        result = ContractValidationResult(
            run_id="run-001",
            checks=checks,
            total_checks=2,
            passed_checks=1,
            failed_checks=1,
        )
        assert len(result.checks) == 2
        assert result.total_checks == 2
        assert result.passed_checks == 1
        assert result.failed_checks == 1

    def test_json_round_trip(self) -> None:
        result = ContractValidationResult(
            run_id="run-001",
            checks=[
                ContractCheckResult(
                    check_id="CHECK-VAL-001",
                    domain="validation",
                    status="pass",
                )
            ],
            total_checks=1,
            passed_checks=1,
        )
        j = result.model_dump_json()
        result2 = ContractValidationResult.model_validate_json(j)
        assert result == result2


@pytest.mark.unit
class TestContractValidationVerdict:
    """Tests for ContractValidationVerdict."""

    def test_create(self) -> None:
        verdict = ContractVerdict(
            status="PASS", score=100, promotion_recommendation=True
        )
        vv = ContractValidationVerdict(
            run_id="run-001",
            verdict=verdict,
            pattern_id="pat-001",
            promote=True,
            promotion_target="production",
        )
        assert vv.verdict.status == "PASS"
        assert vv.promote is True
        assert vv.promotion_target == "production"


@pytest.mark.unit
class TestContractAttributionRecord:
    """Tests for ContractAttributionRecord."""

    def test_create(self) -> None:
        rec = ContractAttributionRecord(
            record_id="attr-001",
            pattern_id="pat-001",
            proposed_by="agent-x",
            validation_run_id="run-001",
            verdict_status="PASS",
            promoted=True,
            promoted_to="production",
        )
        assert rec.record_id == "attr-001"
        assert rec.promoted is True

    def test_frozen(self) -> None:
        rec = ContractAttributionRecord(record_id="x")
        with pytest.raises(ValidationError):
            rec.record_id = "y"  # type: ignore[misc]


@pytest.mark.unit
class TestValidationCheck:
    """Tests for ValidationCheck enum."""

    def test_values_are_strings(self) -> None:
        for check in ValidationCheck:
            assert isinstance(check.value, str)
            assert check.value.startswith("CHECK-")

    def test_specific_checks_exist(self) -> None:
        assert ValidationCheck.CHECK_PY_001.value == "CHECK-PY-001"
        assert ValidationCheck.CHECK_TEST_001.value == "CHECK-TEST-001"
        assert ValidationCheck.CHECK_VAL_001.value == "CHECK-VAL-001"
        assert ValidationCheck.CHECK_RISK_001.value == "CHECK-RISK-001"
        assert ValidationCheck.CHECK_OUT_001.value == "CHECK-OUT-001"

    def test_is_str_enum(self) -> None:
        assert isinstance(ValidationCheck.CHECK_PY_001, str)
        assert ValidationCheck.CHECK_PY_001 == "CHECK-PY-001"
