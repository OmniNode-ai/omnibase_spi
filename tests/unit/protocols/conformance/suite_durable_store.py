# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Checks every ProtocolDurableStore adapter must pass."""

import asyncio
import threading
from collections.abc import Awaitable, Callable

from omnibase_spi.protocols.storage import ProtocolDurableStore


def check_is_protocol_instance(store: ProtocolDurableStore) -> None:
    assert isinstance(store, ProtocolDurableStore)


async def check_read_absent_is_none(store: ProtocolDurableStore) -> None:
    assert await store.read("absent/entry") is None


async def check_write_atomic_replaces_whole_entry(store: ProtocolDurableStore) -> None:
    await store.write_atomic("d/e", b"first-longer-content")
    assert await store.read("d/e") == b"first-longer-content"
    await store.write_atomic("d/e", b"second")
    assert await store.read("d/e") == b"second"


async def check_append_line_appends_in_order(store: ProtocolDurableStore) -> None:
    await store.append_line("log/rows", "one")
    await store.append_line("log/rows", "two")
    assert await store.read("log/rows") == b"one\ntwo\n"


async def check_append_line_refuses_a_newline(store: ProtocolDurableStore) -> None:
    try:
        await store.append_line("log/bad", "a\nb")
    except ValueError:
        assert await store.read("log/bad") is None
        return
    raise AssertionError("append_line accepted a line holding a newline")


async def check_create_exclusive_keeps_the_first(store: ProtocolDurableStore) -> None:
    assert await store.create_exclusive("permits/p1", b"first") is True
    assert await store.create_exclusive("permits/p1", b"second") is False
    assert await store.read("permits/p1") == b"first"


async def check_create_exclusive_races_leave_one_winner(
    store: ProtocolDurableStore,
) -> None:
    results: list[bool] = []
    gate = threading.Barrier(16)

    def attempt(i: int) -> None:
        gate.wait()
        results.append(
            asyncio.run(store.create_exclusive("race/slot", f"w{i}".encode()))
        )

    threads = [threading.Thread(target=attempt, args=(i,)) for i in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert results.count(True) == 1, results
    assert results.count(False) == 15, results
    winner = await store.read("race/slot")
    assert winner is not None and winner.startswith(b"w")


async def check_concurrent_appends_lose_no_line(store: ProtocolDurableStore) -> None:
    gate = threading.Barrier(8)

    def worker(i: int) -> None:
        gate.wait()
        for j in range(25):
            asyncio.run(store.append_line("log/concurrent", f"w{i}-{j}"))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    data = await store.read("log/concurrent")
    assert data is not None
    lines = data.decode().splitlines()
    assert len(lines) == 200, len(lines)
    assert len(set(lines)) == 200


async def check_list_entries_are_sorted_direct_children(
    store: ProtocolDurableStore,
) -> None:
    await store.write_atomic("tree/b", b"1")
    await store.write_atomic("tree/a", b"1")
    await store.write_atomic("tree/sub/deep", b"1")
    assert await store.list_entries("tree") == ("a", "b", "sub")
    assert await store.list_entries("tree/sub") == ("deep",)
    assert await store.list_entries("no/such/dir") == ()


async def check_remove_reports_whether_it_removed(store: ProtocolDurableStore) -> None:
    await store.write_atomic("rm/x", b"1")
    removed_first = await store.remove("rm/x")
    assert removed_first is True
    after = await store.read("rm/x")
    assert after is None
    removed_again = await store.remove("rm/x")
    assert removed_again is False


CHECKS: tuple[Callable[[ProtocolDurableStore], Awaitable[None] | None], ...] = (
    check_is_protocol_instance,
    check_read_absent_is_none,
    check_write_atomic_replaces_whole_entry,
    check_append_line_appends_in_order,
    check_append_line_refuses_a_newline,
    check_create_exclusive_keeps_the_first,
    check_create_exclusive_races_leave_one_winner,
    check_concurrent_appends_lose_no_line,
    check_list_entries_are_sorted_direct_children,
    check_remove_reports_whether_it_removed,
)
