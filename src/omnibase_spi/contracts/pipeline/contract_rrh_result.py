"""ContractRRHResult -- composes list[ContractCheckResult] + ContractVerdict.

The top-level result of a Release Readiness Handshake (RRH) run, containing
all individual check results and the aggregated verdict.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from omnibase_spi.contracts.shared.contract_check_result import ContractCheckResult
from omnibase_spi.contracts.shared.contract_verdict import ContractVerdict


class ContractRRHResult(BaseModel):
    """Result of a Release Readiness Handshake (RRH) run.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        run_id: Correlation ID for the pipeline run.
        checks: Individual check results.
        verdict: Aggregated verdict computed from the checks.
        duration_ms: Wall-clock time for the entire RRH run.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    run_id: str = Field(
        default="",
        description="Correlation ID for the pipeline run.",
    )
    checks: list[ContractCheckResult] = Field(
        default_factory=list,
        description="Individual check results.",
    )
    verdict: ContractVerdict = Field(
        ...,
        description="Aggregated verdict computed from the checks.",
    )
    duration_ms: float | None = Field(
        default=None,
        description="Wall-clock time for the entire RRH run.",
    )
