# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for ProtocolProjectionDatabase and ProtocolProjectionDatabaseSync protocols.

Validates that both protocols:
- Are properly runtime checkable
- Define required methods with correct signatures
- Cannot be instantiated directly
- Work correctly with isinstance checks for compliant/non-compliant classes
"""

from __future__ import annotations

from typing import Any, ClassVar

import pytest

from omnibase_spi.protocols.projections.protocol_projection_database import (
    ProtocolProjectionDatabase,
)
from omnibase_spi.protocols.projections.protocol_projection_database_sync import (
    ProtocolProjectionDatabaseSync,
)


class CompliantAsyncDatabase:
    """Fully compliant implementation of ProtocolProjectionDatabase."""

    async def execute(self, query: str, *params: Any) -> list[dict[str, Any]]:
        return []

    async def execute_many(
        self, query: str, params_list: list[tuple[Any, ...]]
    ) -> None:
        pass

    async def fetchval(self, query: str, *params: Any) -> Any:
        return None

    async def close(self) -> None:
        pass


class IncompliantAsyncDatabase:
    """Missing execute_many — does not satisfy ProtocolProjectionDatabase."""

    async def execute(self, query: str, *params: Any) -> list[dict[str, Any]]:
        return []

    async def fetchval(self, query: str, *params: Any) -> Any:
        return None

    async def close(self) -> None:
        pass


class CompliantSyncDatabase:
    """Fully compliant implementation of ProtocolProjectionDatabaseSync."""

    synchronous_execution: ClassVar[bool] = True

    def upsert(self, table: str, conflict_key: str, row: dict[str, object]) -> bool:
        return True

    def query(
        self, table: str, filters: dict[str, object] | None = None
    ) -> list[dict[str, object]]:
        return []


class IncompliantSyncDatabase:
    """Missing query — does not satisfy ProtocolProjectionDatabaseSync."""

    def upsert(self, table: str, conflict_key: str, row: dict[str, object]) -> bool:
        return True


class TestProtocolProjectionDatabase:
    def test_is_runtime_checkable(self) -> None:
        compliant = CompliantAsyncDatabase()
        assert isinstance(compliant, ProtocolProjectionDatabase)

    def test_non_compliant_fails_isinstance(self) -> None:
        incompliant = IncompliantAsyncDatabase()
        assert not isinstance(incompliant, ProtocolProjectionDatabase)

    def test_plain_object_fails_isinstance(self) -> None:
        assert not isinstance(object(), ProtocolProjectionDatabase)

    def test_required_methods_defined(self) -> None:
        for method in ("execute", "execute_many", "fetchval", "close"):
            assert hasattr(ProtocolProjectionDatabase, method)

    def test_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError):
            ProtocolProjectionDatabase()  # type: ignore[misc]

    def test_exported_from_projections_package(self) -> None:
        from omnibase_spi.protocols.projections import (
            ProtocolProjectionDatabase as Imported,
        )

        assert Imported is ProtocolProjectionDatabase

    def test_exported_from_protocols_package(self) -> None:
        from omnibase_spi.protocols import ProtocolProjectionDatabase as Imported

        assert Imported is ProtocolProjectionDatabase


class TestProtocolProjectionDatabaseSync:
    def test_is_runtime_checkable(self) -> None:
        compliant = CompliantSyncDatabase()
        assert isinstance(compliant, ProtocolProjectionDatabaseSync)

    def test_non_compliant_fails_isinstance(self) -> None:
        incompliant = IncompliantSyncDatabase()
        assert not isinstance(incompliant, ProtocolProjectionDatabaseSync)

    def test_plain_object_fails_isinstance(self) -> None:
        assert not isinstance(object(), ProtocolProjectionDatabaseSync)

    def test_required_methods_defined(self) -> None:
        for method in ("upsert", "query"):
            assert hasattr(ProtocolProjectionDatabaseSync, method)

    def test_declares_synchronous_execution_contract(self) -> None:
        assert "synchronous_execution" in ProtocolProjectionDatabaseSync.__annotations__

    def test_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError):
            ProtocolProjectionDatabaseSync()  # type: ignore[misc]

    def test_exported_from_projections_package(self) -> None:
        from omnibase_spi.protocols.projections import (
            ProtocolProjectionDatabaseSync as Imported,
        )

        assert Imported is ProtocolProjectionDatabaseSync

    def test_exported_from_protocols_package(self) -> None:
        from omnibase_spi.protocols import ProtocolProjectionDatabaseSync as Imported

        assert Imported is ProtocolProjectionDatabaseSync
