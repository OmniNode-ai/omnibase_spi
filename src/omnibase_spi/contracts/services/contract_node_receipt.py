# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ProtocolNodeReceipt — frozen wire model for skill/node invocation outcomes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

_SCHEMA_VERSION = "1.0"


class ProtocolNodeReceipt(BaseModel):
    """Immutable wire record produced after each node invocation.

    A receipt with ``success=False`` MUST carry a non-None ``error_type``.
    An empty ``{}`` receipt does not satisfy DoD validation.

    Fields align with Amendment A1 of OMN-8748/OMN-8737.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(default=_SCHEMA_VERSION)
    node_id: str
    correlation_id: UUID
    action_taken: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str
    side_effect_summary: str = ""
    target_entity_ids: list[str] = Field(default_factory=list)
    dry_run: bool = False
    evidence_references: list[str] = Field(default_factory=list)
    error_type: str | None = None
    output: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_failure_has_error_type(self) -> "ProtocolNodeReceipt":
        if self.status == "failure" and self.error_type is None:
            raise ValueError("ProtocolNodeReceipt with status='failure' requires error_type")
        return self
