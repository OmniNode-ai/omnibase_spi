"""Stable auth decision reason codes.

Defines the canonical set of authorization reason codes used in
:class:`ContractWorkAuthorization.reason_code`.

This module must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from enum import StrEnum


class AuthReasonCode(StrEnum):
    """Authorization decision reason codes.

    Used to explain why an authorization decision was made in
    a machine-readable way.
    """

    # -- Allow reasons -----------------------------------------------------
    ALLOW_DEFAULT = "ALLOW_DEFAULT"
    """Operation is allowed by default policy."""

    ALLOW_EXPLICIT = "ALLOW_EXPLICIT"
    """Operation is explicitly allowed by configuration."""

    ALLOW_OVERRIDE = "ALLOW_OVERRIDE"
    """Operation allowed via human override."""

    # -- Deny reasons ------------------------------------------------------
    DENY_SCOPE = "DENY_SCOPE"
    """Operation is outside the authorized scope."""

    DENY_CROSS_REPO = "DENY_CROSS_REPO"
    """Operation would affect a different repository."""

    DENY_DESTRUCTIVE = "DENY_DESTRUCTIVE"
    """Operation is destructive and not authorized."""

    DENY_RATE_LIMIT = "DENY_RATE_LIMIT"
    """Too many operations in the current window."""

    DENY_POLICY = "DENY_POLICY"
    """Operation denied by a policy rule."""

    DENY_EXPIRED = "DENY_EXPIRED"
    """Authorization grant has expired."""

    # -- Escalate reasons --------------------------------------------------
    ESCALATE_HUMAN_REQUIRED = "ESCALATE_HUMAN_REQUIRED"
    """Operation requires human approval."""

    ESCALATE_RISK = "ESCALATE_RISK"
    """Operation exceeds risk threshold for automated approval."""

    ESCALATE_AMBIGUOUS = "ESCALATE_AMBIGUOUS"
    """Authorization policy is ambiguous; human decision needed."""
