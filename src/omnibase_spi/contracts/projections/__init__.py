# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Wire-format contracts for the projection boundary.

These are frozen Pydantic models used as data contracts across the
synchronous projection write boundary (internal issue).
"""

from omnibase_spi.contracts.projections.contract_projection_result import (
    ContractProjectionResult,
)

__all__ = [
    "ContractProjectionResult",
]
