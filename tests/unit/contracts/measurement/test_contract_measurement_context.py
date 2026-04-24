# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for model_id and producer_kind fields on ContractMeasurementContext.

internal issue: Add model attribution fields to ContractMeasurementContext.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.measurement.contract_measurement_context import (
    ContractMeasurementContext,
    derive_baseline_key,
)


@pytest.mark.unit
class TestMeasurementContextModelAttribution:
    """Tests for model_id and producer_kind on ContractMeasurementContext."""

    def test_measurement_context_model_attribution(self) -> None:
        ctx = ContractMeasurementContext(
            ticket_id="internal issue",
            repo_id="omnibase_core",
            model_id="claude-sonnet-4-20250514",
            producer_kind="agent",
        )
        assert ctx.model_id == "claude-sonnet-4-20250514"
        assert ctx.producer_kind == "agent"

    def test_measurement_context_defaults(self) -> None:
        ctx = ContractMeasurementContext(
            ticket_id="internal issue", repo_id="omnibase_core"
        )
        assert ctx.model_id == ""
        assert ctx.producer_kind == "unknown"

    def test_measurement_context_producer_kind_validation(self) -> None:
        with pytest.raises(ValidationError):
            ContractMeasurementContext(
                ticket_id="internal issue",
                repo_id="omnibase_core",
                producer_kind="bot",  # type: ignore[arg-type]
            )

    def test_baseline_key_unchanged_by_model(self) -> None:
        ctx1 = ContractMeasurementContext(
            ticket_id="internal issue", repo_id="r", model_id="a"
        )
        ctx2 = ContractMeasurementContext(
            ticket_id="internal issue", repo_id="r", model_id="b"
        )
        assert derive_baseline_key(ctx1) == derive_baseline_key(ctx2)
