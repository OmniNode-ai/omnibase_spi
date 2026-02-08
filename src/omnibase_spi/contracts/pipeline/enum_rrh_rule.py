"""Stable RRH rule IDs (RRH-xxxx).

Defines the canonical set of RRH (Release Readiness Handshake) rule
identifiers.  These IDs are stable across versions and used in
:class:`ContractCheckResult.check_id`.

This module must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from enum import Enum


class RRHRule(str, Enum):
    """Stable RRH rule identifiers.

    Prefixed with ``RRH-`` followed by a numeric code.
    1xxx = preflight environment validation.
    """

    # -- Preflight environment validation (1xxx) --------------------------
    RRH_1001 = "RRH-1001"
    """Python version meets minimum requirement."""

    RRH_1002 = "RRH-1002"
    """Poetry lock file is in sync with pyproject.toml."""

    RRH_1003 = "RRH-1003"
    """Virtual environment is active and correct."""

    RRH_1004 = "RRH-1004"
    """Required dev dependencies are installed."""

    RRH_1005 = "RRH-1005"
    """Pre-commit hooks are installed."""

    RRH_1101 = "RRH-1101"
    """Ruff lint passes with zero errors."""

    RRH_1102 = "RRH-1102"
    """Ruff format check passes."""

    RRH_1103 = "RRH-1103"
    """Mypy strict type check passes."""

    RRH_1201 = "RRH-1201"
    """Unit tests pass."""

    RRH_1202 = "RRH-1202"
    """Integration tests pass."""

    RRH_1203 = "RRH-1203"
    """Test coverage meets threshold."""

    RRH_1301 = "RRH-1301"
    """No namespace isolation violations."""

    RRH_1302 = "RRH-1302"
    """Naming pattern validation passes."""

    RRH_1303 = "RRH-1303"
    """Architecture constraints satisfied."""

    RRH_1401 = "RRH-1401"
    """Git working tree is clean."""

    RRH_1402 = "RRH-1402"
    """Branch is up to date with remote."""

    RRH_1403 = "RRH-1403"
    """No merge conflicts detected."""
