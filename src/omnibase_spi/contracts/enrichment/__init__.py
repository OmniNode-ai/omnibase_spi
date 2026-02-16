"""Enrichment contracts for context enrichment operations.

This module provides frozen, high-integrity wire-format contracts for
context enrichment results.  All enrichment operations return
:class:`ContractEnrichmentResult`, providing a uniform output shape
for downstream measurement and audit pipelines.

All contracts use ``ConfigDict(frozen=True, extra="forbid")`` with an
explicit ``extensions: dict[str, Any]`` escape hatch for forward-compatible
extension data.

These contracts must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from omnibase_spi.contracts.enrichment.contract_enrichment_result import (
    ContractEnrichmentResult,
)

__all__ = [
    "ContractEnrichmentResult",
]
