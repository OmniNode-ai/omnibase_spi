"""Delegation contracts for the ONEX delegation pipeline.

This module provides frozen, high-integrity wire-format contracts for
delegation handler output.  All delegation handlers MUST return
:class:`ContractDelegatedResponse`, preventing format fragmentation
across handlers.

All contracts use ``ConfigDict(frozen=True, extra="forbid")`` with an
explicit ``extensions: dict[str, Any]`` escape hatch for forward-compatible
extension data.

These contracts must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from omnibase_spi.contracts.delegation.contract_attachment import (
    ContractAttachment,
)
from omnibase_spi.contracts.delegation.contract_compliance_result import (
    ContractComplianceResult,
)
from omnibase_spi.contracts.delegation.contract_delegated_response import (
    ContractDelegatedResponse,
)
from omnibase_spi.contracts.delegation.contract_delegation_attribution import (
    ContractDelegationAttribution,
)

__all__ = [
    "ContractAttachment",
    "ContractComplianceResult",
    "ContractDelegatedResponse",
    "ContractDelegationAttribution",
]
