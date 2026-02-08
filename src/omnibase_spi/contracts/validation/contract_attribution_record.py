"""ContractAttributionRecord -- closed-loop attribution chain.

Records the provenance chain for a validated pattern: who proposed it,
what validation it went through, and what the outcome was.  Enables
audit trails and closed-loop quality tracking.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ContractAttributionRecord(BaseModel):
    """Closed-loop attribution record for a validated pattern.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        record_id: Unique identifier for this attribution record.
        pattern_id: Pattern candidate this record tracks.
        proposed_by: Who proposed the pattern (agent ID, user name).
        proposed_at_iso: ISO-8601 timestamp of proposal.
        validation_run_id: Validation run that assessed this pattern.
        verdict_status: Final verdict status (PASS/FAIL/QUARANTINE).
        promoted: Whether the pattern was promoted.
        promoted_at_iso: ISO-8601 timestamp of promotion (if promoted).
        promoted_to: Target of promotion (e.g. 'production', 'staging').
        metadata: Arbitrary metadata for the attribution chain.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    record_id: str = Field(
        ...,
        description="Unique identifier for this attribution record.",
    )
    pattern_id: str = Field(
        default="",
        description="Pattern candidate this record tracks.",
    )
    proposed_by: str = Field(
        default="",
        description="Who proposed the pattern (agent ID, user name).",
    )
    proposed_at_iso: str = Field(
        default="",
        description="ISO-8601 timestamp of proposal.",
    )
    validation_run_id: str = Field(
        default="",
        description="Validation run that assessed this pattern.",
    )
    verdict_status: Literal["PASS", "FAIL", "QUARANTINE", ""] = Field(
        default="",
        description="Final verdict status (PASS/FAIL/QUARANTINE).",
    )
    promoted: bool = Field(
        default=False,
        description="Whether the pattern was promoted.",
    )
    promoted_at_iso: str = Field(
        default="",
        description="ISO-8601 timestamp of promotion (if promoted).",
    )
    promoted_to: str = Field(
        default="",
        description="Target of promotion (e.g. 'production', 'staging').",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata for the attribution chain.",
    )
