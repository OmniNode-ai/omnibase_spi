# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Checks every ProtocolTreeLock adapter must pass."""

import threading
from collections.abc import Callable

from omnibase_spi.protocols.runtime import ProtocolTreeLock


def check_is_protocol_instance(lock: ProtocolTreeLock) -> None:
    assert isinstance(lock, ProtocolTreeLock)


def check_acquire_grants_a_token_and_a_second_acquire_is_held(
    lock: ProtocolTreeLock,
) -> None:
    token = lock.acquire("lane.repo")
    assert token
    assert lock.inspect("lane.repo") == token
    assert lock.acquire("lane.repo") is None
    assert lock.inspect("lane.repo") == token


def check_release_by_token_frees_the_key(lock: ProtocolTreeLock) -> None:
    token = lock.acquire("k1")
    assert token
    assert lock.release("k1", token) is True
    assert lock.inspect("k1") is None
    assert lock.acquire("k1")


def check_a_stale_token_leaves_the_new_holder(lock: ProtocolTreeLock) -> None:
    old = lock.acquire("k2")
    assert old
    assert lock.release("k2", old) is True
    new = lock.acquire("k2")
    assert new and new != old
    assert lock.release("k2", old) is False
    assert lock.inspect("k2") == new


def check_release_of_a_free_or_unknown_key_is_false(lock: ProtocolTreeLock) -> None:
    assert lock.release("never-held", "no-such-token") is False
    assert lock.inspect("never-held") is None


def check_keys_are_independent(lock: ProtocolTreeLock) -> None:
    a = lock.acquire("ka")
    b = lock.acquire("kb")
    assert a and b and a != b


def check_racing_acquires_leave_one_holder(lock: ProtocolTreeLock) -> None:
    results: list[str | None] = []
    gate = threading.Barrier(16)

    def attempt() -> None:
        gate.wait()
        results.append(lock.acquire("race"))

    threads = [threading.Thread(target=attempt) for _ in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    granted = [t for t in results if t is not None]
    assert len(granted) == 1, results
    assert lock.inspect("race") == granted[0]


CHECKS: tuple[Callable[[ProtocolTreeLock], None], ...] = (
    check_is_protocol_instance,
    check_acquire_grants_a_token_and_a_second_acquire_is_held,
    check_release_by_token_frees_the_key,
    check_a_stale_token_leaves_the_new_holder,
    check_release_of_a_free_or_unknown_key_is_false,
    check_keys_are_independent,
    check_racing_acquires_leave_one_holder,
)
