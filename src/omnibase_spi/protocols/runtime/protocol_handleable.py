# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Protocol describing an awaitable ``handle`` entry point.

Any object implementing an ``async def handle(envelope) -> object | None``
method structurally satisfies this protocol. The auto-wiring engine uses
it to structurally type-check handler instances before registering them
with the dispatch engine.

Note:
    ``@runtime_checkable`` verifies only the structural presence of a
    ``handle`` method — it does NOT guarantee the attribute is an
    ``async`` function. A synchronous ``def handle(...)`` will still pass
    ``isinstance(obj, ProtocolHandleable)`` and fail later when awaited.
    Callers that need to enforce coroutine-ness MUST additionally check
    ``inspect.iscoroutinefunction(obj.handle)`` (or equivalent) before
    dispatch.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolHandleable(Protocol):
    """Protocol for objects with an async ``handle()`` method."""

    async def handle(self, envelope: object) -> object | None:
        """Handle a runtime envelope.

        Args:
            envelope: Opaque envelope passed by the dispatcher. Concrete
                implementations narrow the type in their own signatures.

        Returns:
            A handler result payload, or ``None`` when the handler
            intentionally produces no output.

        Raises:
            Exception: Implementations may raise domain or runtime
                failures; the dispatcher is responsible for translating
                them into envelopes.
        """
        ...
