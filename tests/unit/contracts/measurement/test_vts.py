# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for ContractPrValidationRollup model and VTS computation.

OMN-3926: Create ContractPrValidationRollup and VTS computation functions.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.measurement.contract_pr_validation_rollup import (
    ContractPrScope,
    ContractPrValidationRollup,
    ContractValidationTax,
)
from omnibase_spi.contracts.measurement.vts import compute_vts, compute_vts_per_kloc


@pytest.mark.unit
class TestContractValidationTax:
    """Tests for ContractValidationTax model."""

    def test_defaults(self) -> None:
        tax = ContractValidationTax()
        assert tax.blocking_failures == 0
        assert tax.warn_findings == 0
        assert tax.reruns == 0
        assert tax.validator_runtime_ms == 0
        assert tax.human_escalations == 0
        assert tax.autofix_successes == 0
        assert tax.time_to_green_ms == 0

    def test_frozen(self) -> None:
        tax = ContractValidationTax(blocking_failures=1)
        with pytest.raises(ValidationError):
            tax.blocking_failures = 2  # type: ignore[misc]


@pytest.mark.unit
class TestVtsComputation:
    """Tests for VTS computation functions."""

    def test_vts_computation(self) -> None:
        tax = ContractValidationTax(
            blocking_failures=2,
            warn_findings=7,
            reruns=4,
            validator_runtime_ms=182000,
            human_escalations=1,
            autofix_successes=3,
        )
        vts = compute_vts(tax)
        assert vts == 149.0

    def test_vts_unit_conversion_explicit(self) -> None:
        tax = ContractValidationTax(validator_runtime_ms=60000)
        vts = compute_vts(tax)
        assert vts == 30.0

    def test_vts_per_kloc_above_1k(self) -> None:
        assert compute_vts_per_kloc(100.0, 2000) == 50.0

    def test_vts_per_kloc_below_1k_floors_to_1(self) -> None:
        assert compute_vts_per_kloc(100.0, 5) == 100.0
        assert compute_vts_per_kloc(100.0, 900) == 100.0


@pytest.mark.unit
class TestContractPrValidationRollup:
    """Tests for ContractPrValidationRollup model."""

    def test_rollup_model_frozen(self) -> None:
        rollup = ContractPrValidationRollup(
            repo_id="core",
            run_id="abc",
            model_id="sonnet",
        )
        with pytest.raises(ValidationError):
            rollup.repo_id = "changed"  # type: ignore[misc]

    def test_rollup_producer_kind_constrained(self) -> None:
        with pytest.raises(ValidationError):
            ContractPrValidationRollup(
                repo_id="core",
                run_id="abc",
                model_id="sonnet",
                producer_kind="bot",  # type: ignore[arg-type]
            )

    def test_rollup_status_values(self) -> None:
        final = ContractPrValidationRollup(
            repo_id="core",
            run_id="a",
            model_id="m",
            rollup_status="final",
        )
        partial = ContractPrValidationRollup(
            repo_id="core",
            run_id="b",
            model_id="m",
            rollup_status="partial",
        )
        assert final.rollup_status == "final"
        assert partial.rollup_status == "partial"

    def test_rollup_defaults(self) -> None:
        rollup = ContractPrValidationRollup(
            repo_id="core",
            run_id="abc",
            model_id="sonnet",
        )
        assert rollup.schema_version == "1.0"
        assert rollup.metric_version == "v1"
        assert rollup.pr_id == ""
        assert rollup.pr_url == ""
        assert rollup.ticket_id == ""
        assert rollup.producer_kind == "unknown"
        assert rollup.rollup_status == "final"
        assert rollup.scope == ContractPrScope()
        assert rollup.tax == ContractValidationTax()
        assert rollup.vts == 0.0
        assert rollup.vts_per_kloc == 0.0
        assert rollup.phase_count == 0
        assert rollup.extensions == {}

    def test_rollup_json_round_trip(self) -> None:
        rollup = ContractPrValidationRollup(
            repo_id="core",
            run_id="abc",
            model_id="sonnet",
            producer_kind="agent",
            tax=ContractValidationTax(blocking_failures=1),
            scope=ContractPrScope(files_changed=5, lines_changed=200),
            vts=10.0,
            vts_per_kloc=50.0,
        )
        j = rollup.model_dump_json()
        rollup2 = ContractPrValidationRollup.model_validate_json(j)
        assert rollup == rollup2

    def test_rollup_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractPrValidationRollup(
                repo_id="core",
                run_id="abc",
                model_id="sonnet",
                bad_field="nope",  # type: ignore[call-arg]
            )
