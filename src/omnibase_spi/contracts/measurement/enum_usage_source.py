"""ContractEnumUsageSource -- token usage provenance.

Indicates whether LLM token usage data was reported by the provider API,
estimated locally (e.g. via a tokenizer), or is entirely missing.

This module must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from enum import StrEnum


class ContractEnumUsageSource(StrEnum):
    """Provenance of LLM token usage data.

    Members:
        API: Usage data reported directly by the LLM provider API.
        ESTIMATED: Usage data estimated locally (e.g. via tokenizer counting).
        MISSING: No usage data available from any source.
    """

    API = "api"
    """Usage data reported directly by the LLM provider API."""

    ESTIMATED = "estimated"
    """Usage data estimated locally (e.g. via tokenizer counting)."""

    MISSING = "missing"
    """No usage data available from any source."""
