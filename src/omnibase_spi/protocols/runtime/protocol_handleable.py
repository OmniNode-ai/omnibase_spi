# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Protocol describing an awaitable ``handle`` entry point.

Any object implementing an ``async def handle(envelope) -> object | None``
method structurally satisfies this protocol. Used by the auto-wiring engine
to validate handler instances before registering them with the dispatch
engine.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolHandleable(Protocol):
    """Protocol for objects with an async ``handle()`` method."""

    async def handle(self, envelope: object) -> object | None: ...
