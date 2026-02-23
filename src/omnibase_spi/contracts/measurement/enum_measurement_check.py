"""Stable measurement check IDs (CHECK-MEAS-xxx).

Defines the canonical set of measurement check identifiers used in
:class:`ContractCheckResult.check_id` for the measurement domain.

This module must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from enum import StrEnum


class MeasurementCheck(StrEnum):
    """Stable measurement check identifiers.

    Organized by prefix CHECK-MEAS-xxx for measurement-domain checks.

    Members:
        CHECK_MEAS_001: Phase duration within expected bounds.
        CHECK_MEAS_002: Cost metrics within budget.
        CHECK_MEAS_003: Test pass rate meets threshold.
        CHECK_MEAS_004: Outcome classification is consistent with phase result.
        CHECK_MEAS_005: Artifact pointers are resolvable.
        CHECK_MEAS_006: Promotion gate evidence is sufficient.
    """

    CHECK_MEAS_001 = "CHECK-MEAS-001"
    """Phase duration within expected bounds."""

    CHECK_MEAS_002 = "CHECK-MEAS-002"
    """Cost metrics within budget."""

    CHECK_MEAS_003 = "CHECK-MEAS-003"
    """Test pass rate meets threshold."""

    CHECK_MEAS_004 = "CHECK-MEAS-004"
    """Outcome classification is consistent with phase result."""

    CHECK_MEAS_005 = "CHECK-MEAS-005"
    """Artifact pointers are resolvable."""

    CHECK_MEAS_006 = "CHECK-MEAS-006"
    """Promotion gate evidence is sufficient."""
