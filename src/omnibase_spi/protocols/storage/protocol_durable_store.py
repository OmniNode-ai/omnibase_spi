# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Protocol for a durable store of named byte blobs and line logs.

A node that keeps state across runs (a record, a permit, a lease table, a log of
lines) takes a durable store instead of opening files itself, so the same node
runs over an in-memory store in a test and over a filesystem or other durable
store in a lab or production binding. Paths are ``/``-separated strings relative
to the store's root; a directory exists while it holds an entry.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolDurableStore(Protocol):
    """Six operations on named entries: read, write, append, create, list, remove."""

    async def read(self, path: str) -> bytes | None:
        """Return the entry's bytes, or None when the entry does not exist."""
        ...

    async def write_atomic(self, path: str, data: bytes) -> None:
        """Replace the whole entry with ``data``; a reader sees the old or the new bytes, never a mix."""
        ...

    async def append_line(self, path: str, line: str) -> None:
        """Append ``line`` and a newline, creating the entry if absent; ``line`` holds no newline."""
        ...

    async def create_exclusive(self, path: str, data: bytes) -> bool:
        """Create the entry holding ``data``; return False and change nothing when it exists.

        Of any number of concurrent calls for one path, exactly one returns True.
        """
        ...

    async def list_entries(self, directory: str) -> tuple[str, ...]:
        """Return the sorted names directly inside ``directory``; empty when it does not exist."""
        ...

    async def remove(self, path: str) -> bool:
        """Remove the entry; return False when it did not exist."""
        ...


__all__ = ["ProtocolDurableStore"]
