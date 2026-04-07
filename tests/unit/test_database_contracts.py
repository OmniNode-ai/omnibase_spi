# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for database wire-format contracts."""

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.database import ModelQueryResult, ModelTransactionResult


class TestModelQueryResult:
    def test_minimal(self) -> None:
        result = ModelQueryResult(row_count=0, duration_ms=1.5)
        assert result.rows == []
        assert result.columns == []
        assert result.row_count == 0
        assert result.duration_ms == 1.5

    def test_with_data(self) -> None:
        result = ModelQueryResult(
            rows=[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
            columns=["id", "name"],
            row_count=2,
            duration_ms=12.3,
        )
        assert len(result.rows) == 2
        assert result.columns == ["id", "name"]

    def test_frozen(self) -> None:
        result = ModelQueryResult(row_count=0, duration_ms=1.0)
        with pytest.raises(ValidationError):
            result.row_count = 5  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        with pytest.raises(ValidationError):
            ModelQueryResult(
                row_count=0,
                duration_ms=1.0,
                extra_field="bad",  # type: ignore[call-arg]
            )


class TestModelTransactionResult:
    def test_committed(self) -> None:
        result = ModelTransactionResult(
            committed=True, operations_count=3, duration_ms=45.0
        )
        assert result.committed is True
        assert result.operations_count == 3
        assert result.duration_ms == 45.0

    def test_rolled_back(self) -> None:
        result = ModelTransactionResult(
            committed=False, operations_count=1, duration_ms=2.0
        )
        assert result.committed is False

    def test_frozen(self) -> None:
        result = ModelTransactionResult(
            committed=True, operations_count=1, duration_ms=1.0
        )
        with pytest.raises(ValidationError):
            result.committed = False  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        with pytest.raises(ValidationError):
            ModelTransactionResult(
                committed=True,
                operations_count=1,
                duration_ms=1.0,
                extra="bad",  # type: ignore[call-arg]
            )
