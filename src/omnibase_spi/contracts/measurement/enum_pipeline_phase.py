"""ContractEnumPipelinePhase -- canonical pipeline phases.

Defines the five discrete phases a measurement pipeline execution passes
through.  Each phase maps to a ``ContractPhaseMetrics`` instance.

This module must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from enum import StrEnum


class ContractEnumPipelinePhase(StrEnum):
    """Canonical pipeline phases for measurement tracking.

    Members:
        PLAN: Planning and specification phase.
        IMPLEMENT: Code generation / implementation phase.
        VERIFY: Testing and verification phase.
        REVIEW: Code review phase.
        RELEASE: Release and deployment phase.
    """

    PLAN = "plan"
    """Planning and specification phase."""

    IMPLEMENT = "implement"
    """Code generation / implementation phase."""

    VERIFY = "verify"
    """Testing and verification phase."""

    REVIEW = "review"
    """Code review phase."""

    RELEASE = "release"
    """Release and deployment phase."""
