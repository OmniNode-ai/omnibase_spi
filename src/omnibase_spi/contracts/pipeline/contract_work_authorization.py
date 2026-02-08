"""ContractWorkAuthorization -- auth grant wire format.

Represents the result of an authorization decision: whether the agent is
allowed to proceed with a particular operation, and under what conditions.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ContractWorkAuthorization(BaseModel):
    """Authorization grant or denial for a pipeline operation.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        decision: Whether the operation is authorized.
        reason_code: Machine-readable reason for the decision.
        reason: Human-readable explanation.
        scope: What scope the authorization covers.
        expires_at_iso: ISO-8601 expiry timestamp (empty = no expiry).
        conditions: Key-value conditions attached to the grant.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    decision: Literal["allow", "deny", "escalate"] = Field(
        ...,
        description="Whether the operation is authorized.",
    )
    reason_code: str = Field(
        default="",
        description="Machine-readable reason code for the decision.",
    )
    reason: str = Field(
        default="",
        description="Human-readable explanation.",
    )
    scope: str = Field(
        default="",
        description="What scope the authorization covers.",
    )
    expires_at_iso: str = Field(
        default="",
        description="ISO-8601 expiry timestamp (empty = no expiry).",
    )
    conditions: dict[str, str] = Field(
        default_factory=dict,
        description="Key-value conditions attached to the grant.",
    )
