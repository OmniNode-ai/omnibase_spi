"""Validation Tax Score (VTS) computation functions.

Pure functions that compute the VTS from ``ContractValidationTax`` counters.
Kept separate from the contract model so that the model remains a pure data
object with no business logic.

This module must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from omnibase_spi.contracts.measurement.contract_pr_validation_rollup import (
    ContractValidationTax,
)

DEFAULT_VTS_WEIGHTS: dict[str, float] = {
    "blocking_failures": 10.0,
    "warn_findings": 1.0,
    "reruns": 5.0,
    "validator_runtime_s": 0.5,
    "human_escalations": 20.0,
    "autofix_successes": -3.0,
}


def compute_vts(
    tax: ContractValidationTax,
    weights: dict[str, float] | None = None,
) -> float:
    """Compute the Validation Tax Score from raw counters.

    Args:
        tax: Raw validation tax counters.
        weights: Optional weight overrides. Defaults to ``DEFAULT_VTS_WEIGHTS``.

    Returns:
        The weighted VTS value (lower is better).
    """
    w = weights or DEFAULT_VTS_WEIGHTS
    return (
        w["blocking_failures"] * tax.blocking_failures
        + w["warn_findings"] * tax.warn_findings
        + w["reruns"] * tax.reruns
        + w["validator_runtime_s"] * (tax.validator_runtime_ms / 1000)
        + w["human_escalations"] * tax.human_escalations
        + w["autofix_successes"] * tax.autofix_successes
    )


def compute_vts_per_kloc(vts: float, lines_changed: int) -> float:
    """Normalise VTS per 1000 lines changed.

    For PRs with fewer than 1000 lines, the denominator floors to 1
    (i.e. 1 kLOC) to avoid inflating the metric for small changes.

    Args:
        vts: The computed VTS value.
        lines_changed: Total lines changed in the PR.

    Returns:
        VTS normalised per kLOC.
    """
    return vts / max(1, lines_changed // 1000)
