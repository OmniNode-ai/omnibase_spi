# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Transcript store port: one way to read and to mirror transcript files.

A transcript file grows by appending records. The store is a keyed set of such
files, each held with a ``revision`` (the record count of the copy) and the
``sha256`` of its bytes. Handlers behind this port are a directory on a disk
(read side only), an in-memory store (tests) and an object bucket.

The write side is ``put`` and nothing else. No method deletes an object and no
method lowers one: ``put`` is a conditional write decided by the store, so two
overlapping writers cannot move an object's recorded revision down. This follows
the design-review verdict of the mirror's conditional upload model (a put
without the condition, or a read of the recorded revision followed by an
unconditional put, both violate "the recorded revision never decreases").
"""

from collections.abc import Sequence
from typing import Literal, Protocol, runtime_checkable

TranscriptPutOutcome = Literal[
    "stored",
    "unchanged",
    "refused-stale",
    "refused-conflict",
]
"""Result of one conditional put.

- ``stored``: no object was held, or the recorded revision was below the copy's;
  the object and its recorded revision changed together.
- ``unchanged``: an object at the same revision with the same sha256 is held.
- ``refused-stale``: the recorded revision is above the copy's; nothing changed.
- ``refused-conflict``: the recorded revision equals the copy's but the sha256
  differs; nothing changed (a larger revision must be an extension of a smaller
  one, so equal revisions with different content cannot both be right).

A refused put is a normal outcome, not an error, and is not retried with the
same copy.
"""


@runtime_checkable
class ProtocolTranscriptObjectRecord(Protocol):
    """What a store records for one object; never the file content."""

    @property
    def key(self) -> str:
        """Store key (a prefix plus the root-relative path for a mirror)."""
        ...

    @property
    def size_bytes(self) -> int:
        """Byte length of the held copy."""
        ...

    @property
    def revision(self) -> int:
        """Record count of the held copy (the monotonic source revision)."""
        ...

    @property
    def sha256(self) -> str:
        """Lowercase hex sha256 of the held copy's bytes."""
        ...


@runtime_checkable
class ProtocolTranscriptSource(Protocol):
    """Read side of a transcript store: list and read, never write."""

    async def list_objects(
        self, prefix: str
    ) -> Sequence[ProtocolTranscriptObjectRecord]:
        """Records of every object whose key starts with ``prefix``, sorted by key.

        An empty prefix lists everything under the store's own root.
        """
        ...

    async def read(self, key: str) -> bytes:
        """Bytes of the object at ``key``.

        Raises:
            KeyError: when no object is held at ``key``.
            ValueError: when ``key`` is absolute or escapes the store's root.
        """
        ...


@runtime_checkable
class ProtocolTranscriptStore(ProtocolTranscriptSource, Protocol):
    """Transcript store with a write side that can only add or extend.

    The only write method is ``put``. There is no delete and no method that
    replaces an object with a shorter or equal one.
    """

    async def stat(self, key: str) -> ProtocolTranscriptObjectRecord | None:
        """Record of the object at ``key``, or ``None`` when none is held."""
        ...

    async def put(
        self, key: str, content: bytes, revision: int, sha256: str
    ) -> TranscriptPutOutcome:
        """Store ``content`` at ``key`` only if the recorded revision is below ``revision``.

        The condition is decided on the store, atomically with the write, and
        the object's content and its recorded revision change together.

        Args:
            key: Store key.
            content: Bytes of the copy.
            revision: Record count of ``content``.
            sha256: Lowercase hex sha256 of ``content``.

        Returns:
            One of ``TranscriptPutOutcome``.
        """
        ...


__all__ = [
    "ProtocolTranscriptObjectRecord",
    "ProtocolTranscriptSource",
    "ProtocolTranscriptStore",
    "TranscriptPutOutcome",
]
