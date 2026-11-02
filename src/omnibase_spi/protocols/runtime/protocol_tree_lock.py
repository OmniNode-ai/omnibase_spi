# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Protocol for a non-blocking lock on one named tree.

The holder of a grant token is the only party that may change the tree. A caller
that cannot get the lock is told so at once and skips the tree; it never waits.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolTreeLock(Protocol):
    """Acquire without waiting, inspect, and release by token."""

    def acquire(self, key: str) -> str | None:
        """Take the lock on ``key`` without waiting.

        Returns a grant token that no earlier or later grant shares, or None when the
        lock is held ("held").
        """
        ...

    def inspect(self, key: str) -> str | None:
        """Return the token of the grant now holding ``key``, or None when it is free."""
        ...

    def release(self, key: str, token: str) -> bool:
        """Release ``key`` if ``token`` is the current grant; otherwise change nothing.

        Returns False for a stale or unknown token, so a delayed duplicate release
        never frees the lock a later holder owns.
        """
        ...


__all__ = ["ProtocolTreeLock"]
