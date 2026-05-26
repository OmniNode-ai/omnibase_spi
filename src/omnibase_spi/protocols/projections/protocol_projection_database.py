# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for async projection database adapters."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolProjectionDatabase(Protocol):
    """Protocol for async projection database adapters.

    Matches the real adapter interface used by omnimarket projection
    runners (AsyncpgAdapter). Implementations provide parameterized
    query execution over an async connection pool.

    Migrated from omnibase_compat.protocols.protocol_projection_database
    (OMN-12190, removal date 2026-07-01).
    """

    async def execute(self, query: str, *params: Any) -> list[dict[str, Any]]:
        """Execute a parameterized query and return rows as dicts."""
        ...

    async def execute_many(
        self, query: str, params_list: list[tuple[Any, ...]]
    ) -> None:
        """Execute a parameterized query for each set of params."""
        ...

    async def fetchval(self, query: str, *params: Any) -> Any:
        """Execute a query and return a single scalar value."""
        ...

    async def close(self) -> None:
        """Close the connection pool."""
        ...
