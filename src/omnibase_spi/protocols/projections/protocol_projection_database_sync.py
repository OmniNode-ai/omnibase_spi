# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for synchronous projection database adapters."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolProjectionDatabaseSync(Protocol):
    """Protocol for synchronous projection database adapters.

    Matches the sync DatabaseAdapter interface used by omnimarket
    projection handler nodes (upsert/query pattern). For the async
    adapter used by projection runners, see ProtocolProjectionDatabase.

    Migrated from omnibase_compat.protocols.protocol_projection_database_sync
    (OMN-12190, removal date 2026-07-01).
    """

    def upsert(
        self,
        table: str,
        conflict_key: str,
        row: dict[str, object],
    ) -> bool:
        """UPSERT a row. Returns True on success."""
        ...

    def query(
        self,
        table: str,
        filters: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        """Query rows from a table with optional filters."""
        ...
