"""Stable RRH rule IDs (RRH-xxxx).

Defines the canonical set of RRH (Release Readiness Handshake) rule
identifiers.  These IDs are stable across versions and used in
:class:`ContractCheckResult.check_id`.

Group numbering convention:
    10xx = repo checks
    11xx = environment checks
    12xx = kafka checks
    13xx = kubernetes checks
    14xx = toolchain checks
    15xx = cross-checks (branch/ticket)
    16xx = cross-checks (contract fields)
    17xx = repo-boundary checks

This module must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from enum import StrEnum


class RRHRule(StrEnum):
    """Stable RRH rule identifiers.

    Prefixed with ``RRH-`` followed by a numeric code.
    Each group of codes covers a specific validation domain.
    """

    # -- Repo checks (10xx) ---------------------------------------------------
    RRH_1001 = "RRH-1001"
    """Repo clean working tree."""

    RRH_1002 = "RRH-1002"
    """Repo on expected branch."""

    # -- Environment checks (11xx) --------------------------------------------
    RRH_1101 = "RRH-1101"
    """Environment target valid."""

    RRH_1102 = "RRH-1102"
    """Environment kafka_broker configured."""

    # -- Kafka checks (12xx) --------------------------------------------------
    RRH_1201 = "RRH-1201"
    """Kafka broker reachable (conditional)."""

    # -- Kubernetes checks (13xx) ---------------------------------------------
    RRH_1301 = "RRH-1301"
    """Kubernetes context valid (conditional)."""

    # -- Toolchain checks (14xx) ----------------------------------------------
    RRH_1401 = "RRH-1401"
    """Toolchain pre-commit present."""

    RRH_1402 = "RRH-1402"
    """Toolchain ruff present."""

    RRH_1403 = "RRH-1403"
    """Toolchain pytest present (conditional)."""

    RRH_1404 = "RRH-1404"
    """Toolchain mypy present."""

    # -- Cross-checks (15xx) --------------------------------------------------
    RRH_1501 = "RRH-1501"
    """Cross-check branch matches ticket ID."""

    # -- Cross-checks (16xx) --------------------------------------------------
    RRH_1601 = "RRH-1601"
    """Cross-check no disallowed contract fields."""

    # -- Repo-boundary checks (17xx) ------------------------------------------
    RRH_1701 = "RRH-1701"
    """Repo-boundary no cross-repo imports."""
