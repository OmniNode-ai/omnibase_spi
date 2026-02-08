"""ContractEnumResultClassification -- outcome categories.

Classifies the result of a pipeline phase execution into one of five
canonical categories used by outcome metrics and aggregation logic.

This module must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from enum import Enum


class ContractEnumResultClassification(str, Enum):
    """Canonical result categories for phase outcomes.

    Members:
        SUCCESS: Phase completed successfully.
        FAILURE: Phase completed with errors.
        PARTIAL: Phase completed partially (some steps skipped or degraded).
        SKIPPED: Phase was intentionally skipped.
        ERROR: Phase terminated due to an unrecoverable error.
    """

    SUCCESS = "success"
    """Phase completed successfully."""

    FAILURE = "failure"
    """Phase completed with errors."""

    PARTIAL = "partial"
    """Phase completed partially (some steps skipped or degraded)."""

    SKIPPED = "skipped"
    """Phase was intentionally skipped."""

    ERROR = "error"
    """Phase terminated due to an unrecoverable error."""
