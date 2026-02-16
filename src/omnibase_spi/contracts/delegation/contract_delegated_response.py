"""ContractDelegatedResponse -- canonical output for all delegation handlers.

Every delegation handler MUST return this model.  Enforcing a single output
shape prevents format fragmentation and guarantees that downstream consumers
(dashboards, measurement pipelines, audit trails) can process delegation
results uniformly.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from omnibase_spi.contracts.delegation.contract_attachment import (
    ContractAttachment,
)
from omnibase_spi.contracts.delegation.contract_compliance_result import (
    ContractComplianceResult,
)
from omnibase_spi.contracts.delegation.contract_delegation_attribution import (
    ContractDelegationAttribution,
)


class ContractDelegatedResponse(BaseModel):
    """Canonical output contract for all delegation handlers.

    All delegation handlers MUST return this model.  The uniform shape
    prevents format fragmentation across handlers and ensures downstream
    consumers can process delegation results without per-handler adapters.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        rendered_text: Markdown-formatted output from the delegated LLM call.
        attachments: File or data attachments accompanying the response.
        structured_json: Optional structured data returned by the handler.
        attribution: Provenance metadata for the delegated LLM call.
        quality_gate_result: Outcome of a quality-gate evaluation, if one
            was applied.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    rendered_text: str = Field(
        ...,
        min_length=1,
        description="Markdown-formatted output from the delegated LLM call.",
    )
    attachments: list[ContractAttachment] = Field(
        default_factory=list,
        description="File or data attachments accompanying the response.",
    )
    structured_json: dict[str, Any] | None = Field(
        default=None,
        description="Optional structured data returned by the handler.",
    )
    attribution: ContractDelegationAttribution = Field(
        ...,
        description="Provenance metadata for the delegated LLM call.",
    )
    quality_gate_result: ContractComplianceResult | None = Field(
        default=None,
        description="Outcome of a quality-gate evaluation, if one was applied.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )
