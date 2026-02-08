"""Shared contract primitives for the ONEX pipeline and validation systems.

These are foundational data contracts reused across multiple domains:
- Pipeline RRH (Release Readiness Handshake)
- Validation orchestration
- Governance and compliance

All contracts are frozen Pydantic models with forward-compatible deserialization.
"""

from omnibase_spi.contracts.shared.contract_check_result import ContractCheckResult
from omnibase_spi.contracts.shared.contract_verdict import ContractVerdict

__all__ = [
    "ContractCheckResult",
    "ContractVerdict",
]
