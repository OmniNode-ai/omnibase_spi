"""ContractValidationResult -- composes list[ContractCheckResult].

Collects all individual check results from a validation run without
computing a verdict.  The verdict is computed separately in
:class:`ContractValidationVerdict`.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from omnibase_spi.contracts.shared.contract_check_result import ContractCheckResult


class ContractValidationResult(BaseModel):
    """Collection of check results from a validation run.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        run_id: Correlation ID linking to the validation run.
        checks: Individual check results.
        total_checks: Total number of checks executed.
        passed_checks: Number of checks that passed.
        failed_checks: Number of checks that failed.
        skipped_checks: Number of checks that were skipped.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    run_id: str = Field(
        default="",
        description="Correlation ID linking to the validation run.",
    )
    checks: list[ContractCheckResult] = Field(
        default_factory=list,
        description="Individual check results.",
    )
    total_checks: int = Field(
        default=0,
        ge=0,
        description="Total number of checks executed.",
    )
    passed_checks: int = Field(
        default=0,
        ge=0,
        description="Number of checks that passed.",
    )
    failed_checks: int = Field(
        default=0,
        ge=0,
        description="Number of checks that failed.",
    )
    skipped_checks: int = Field(
        default=0,
        ge=0,
        description="Number of checks that were skipped.",
    )
