"""Validation contracts for the ONEX validation orchestration system.

These contracts define wire formats for the validation subsystem:
pattern candidates, validation plans, runs, results, verdicts,
and attribution records.

All contracts are frozen Pydantic models with forward-compatible deserialization.
They must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from omnibase_spi.contracts.validation.contract_attribution_record import (
    ContractAttributionRecord,
)
from omnibase_spi.contracts.validation.contract_pattern_candidate import (
    ContractPatternCandidate,
)
from omnibase_spi.contracts.validation.contract_validation_plan import (
    ContractValidationPlan,
)
from omnibase_spi.contracts.validation.contract_validation_result import (
    ContractValidationResult,
)
from omnibase_spi.contracts.validation.contract_validation_run import (
    ContractValidationRun,
)
from omnibase_spi.contracts.validation.contract_validation_verdict import (
    ContractValidationVerdict,
)
from omnibase_spi.contracts.validation.enum_validation_check import ValidationCheck

__all__ = [
    "ContractAttributionRecord",
    "ContractPatternCandidate",
    "ContractValidationPlan",
    "ContractValidationResult",
    "ContractValidationRun",
    "ContractValidationVerdict",
    "ValidationCheck",
]
