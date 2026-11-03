# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for the transcript store port.

The port's write side is ``put`` only: no method deletes an object and no method
lowers one. A conforming in-memory store decides the condition atomically and a
late put of a shorter copy is refused.
"""

import asyncio
import hashlib
import inspect
from collections.abc import Sequence
from dataclasses import dataclass

import pytest

from omnibase_spi.protocols.storage import (
    ProtocolTranscriptObjectRecord,
    ProtocolTranscriptSource,
    ProtocolTranscriptStore,
    TranscriptPutOutcome,
)

_DELETING_OR_LOWERING = ("delete", "remove", "unlink", "purge", "truncate", "lower")


@dataclass(frozen=True)
class _Record:
    key: str
    size_bytes: int
    revision: int
    sha256: str


class _MemoryStore:
    def __init__(self) -> None:
        self._objects: dict[str, tuple[bytes, _Record]] = {}
        self._lock = asyncio.Lock()

    async def list_objects(
        self, prefix: str
    ) -> Sequence[ProtocolTranscriptObjectRecord]:
        return [
            record
            for key, (_, record) in sorted(self._objects.items())
            if key.startswith(prefix)
        ]

    async def read(self, key: str) -> bytes:
        return self._objects[key][0]

    async def stat(self, key: str) -> ProtocolTranscriptObjectRecord | None:
        held = self._objects.get(key)
        return None if held is None else held[1]

    async def put(
        self, key: str, content: bytes, revision: int, sha256: str
    ) -> TranscriptPutOutcome:
        async with self._lock:
            held = self._objects.get(key)
            if held is not None:
                recorded = held[1]
                if recorded.revision > revision:
                    return "refused-stale"
                if recorded.revision == revision:
                    return (
                        "unchanged" if recorded.sha256 == sha256 else "refused-conflict"
                    )
            self._objects[key] = (content, _Record(key, len(content), revision, sha256))
            return "stored"


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def test_store_protocol_has_no_method_that_deletes_or_lowers() -> None:
    names = {
        name
        for name, member in inspect.getmembers(
            ProtocolTranscriptStore, predicate=inspect.iscoroutinefunction
        )
        if not name.startswith("_")
    }
    assert names == {"list_objects", "read", "stat", "put"}
    for name in names:
        assert not any(word in name for word in _DELETING_OR_LOWERING)


def test_source_protocol_has_no_write_method() -> None:
    names = {
        name
        for name, _ in inspect.getmembers(
            ProtocolTranscriptSource, predicate=inspect.iscoroutinefunction
        )
        if not name.startswith("_")
    }
    assert names == {"list_objects", "read"}


def test_conforming_store_is_runtime_checkable() -> None:
    store = _MemoryStore()
    assert isinstance(store, ProtocolTranscriptStore)
    assert isinstance(store, ProtocolTranscriptSource)
    assert not isinstance(object(), ProtocolTranscriptStore)


@pytest.mark.asyncio
async def test_late_shorter_put_is_refused_and_recorded_revision_does_not_decrease() -> (
    None
):
    store = _MemoryStore()
    short, long = b"a\n" * 10, b"a\n" * 11
    assert await store.put("k", long, 11, _digest(long)) == "stored"
    assert await store.put("k", short, 10, _digest(short)) == "refused-stale"
    held = await store.stat("k")
    assert held is not None
    assert held.revision == 11
    assert await store.read("k") == long


@pytest.mark.asyncio
async def test_equal_revision_same_digest_is_unchanged_and_different_digest_conflicts() -> (
    None
):
    store = _MemoryStore()
    one, other = b"x\n", b"y\n"
    assert await store.put("k", one, 1, _digest(one)) == "stored"
    assert await store.put("k", one, 1, _digest(one)) == "unchanged"
    assert await store.put("k", other, 1, _digest(other)) == "refused-conflict"
    assert await store.read("k") == one


@pytest.mark.asyncio
async def test_missing_object_stat_is_none_and_read_raises_key_error() -> None:
    store = _MemoryStore()
    assert await store.stat("absent") is None
    with pytest.raises(KeyError):
        await store.read("absent")
