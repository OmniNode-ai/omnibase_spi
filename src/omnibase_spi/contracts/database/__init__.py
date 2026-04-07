# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Database wire-format contracts for ProtocolDatabaseConnection return types."""

from omnibase_spi.contracts.database.model_query_result import ModelQueryResult
from omnibase_spi.contracts.database.model_transaction_result import (
    ModelTransactionResult,
)

__all__ = [
    "ModelQueryResult",
    "ModelTransactionResult",
]
