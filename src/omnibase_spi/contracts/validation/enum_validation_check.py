"""Stable validation check IDs (CHECK-xxxx).

Defines the canonical set of validation check identifiers used in
:class:`ContractCheckResult.check_id` for the validation domain.

This module must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from enum import StrEnum


class ValidationCheck(StrEnum):
    """Stable validation check identifiers.

    Organized by prefix:
    - CHECK-PY-xxx:   Python toolchain checks
    - CHECK-TEST-xxx: Test execution checks
    - CHECK-VAL-xxx:  Pipeline integrity checks
    - CHECK-RISK-xxx: Risk gating checks
    - CHECK-OUT-xxx:  Outcome and cost checks
    """

    # -- Python toolchain checks (PY) -------------------------------------
    CHECK_PY_001 = "CHECK-PY-001"
    """Python version compatibility."""

    CHECK_PY_002 = "CHECK-PY-002"
    """Import structure validity."""

    CHECK_PY_003 = "CHECK-PY-003"
    """Type annotation completeness."""

    CHECK_PY_004 = "CHECK-PY-004"
    """Docstring coverage."""

    # -- Test execution checks (TEST) --------------------------------------
    CHECK_TEST_001 = "CHECK-TEST-001"
    """Unit test suite passes."""

    CHECK_TEST_002 = "CHECK-TEST-002"
    """Integration test suite passes."""

    CHECK_TEST_003 = "CHECK-TEST-003"
    """Test coverage meets threshold."""

    CHECK_TEST_004 = "CHECK-TEST-004"
    """No new test regressions."""

    # -- Pipeline integrity checks (VAL) -----------------------------------
    CHECK_VAL_001 = "CHECK-VAL-001"
    """Schema version present on all contracts."""

    CHECK_VAL_002 = "CHECK-VAL-002"
    """No forbidden imports detected."""

    CHECK_VAL_003 = "CHECK-VAL-003"
    """Forward compatibility maintained."""

    CHECK_VAL_004 = "CHECK-VAL-004"
    """Naming conventions respected."""

    # -- Risk gating checks (RISK) -----------------------------------------
    CHECK_RISK_001 = "CHECK-RISK-001"
    """No secrets in committed files."""

    CHECK_RISK_002 = "CHECK-RISK-002"
    """No destructive operations detected."""

    CHECK_RISK_003 = "CHECK-RISK-003"
    """Cross-repo impact assessment."""

    # -- Outcome and cost checks (OUT) -------------------------------------
    CHECK_OUT_001 = "CHECK-OUT-001"
    """LLM token usage within budget."""

    CHECK_OUT_002 = "CHECK-OUT-002"
    """Execution time within limits."""

    CHECK_OUT_003 = "CHECK-OUT-003"
    """Artifact size within limits."""
