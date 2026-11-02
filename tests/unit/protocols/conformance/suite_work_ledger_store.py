# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Checks every ProtocolWorkLedgerStore adapter must pass (OMN-22198).

A real adapter is wrapped in a harness that puts raw rows into the ledger and
records the rows a lane queued on its host.
"""

from collections.abc import Callable
from typing import Protocol

from omnibase_spi.protocols.lane import ProtocolWorkLedgerStore


class LedgerHarness(Protocol):
    store: ProtocolWorkLedgerStore

    def append(self, row: str) -> None: ...

    def queue(self, lane: str, run_id: str, row: str) -> None: ...


def check_is_protocol_instance(h: LedgerHarness) -> None:
    assert isinstance(h.store, ProtocolWorkLedgerStore)


def check_a_lane_with_no_rows_gets_an_empty_tuple(h: LedgerHarness) -> None:
    h.append("STATUS lane=other note=x")
    assert h.store.rows_for_lane("lane-1") == ()
    assert h.store.queued_rows("lane-1", "run-1") == ()


def check_rows_for_lane_are_that_lanes_rows_oldest_first(h: LedgerHarness) -> None:
    h.append("CLAIM lane=lane-1 ticket=T1")
    h.append("STATUS lane=lane-2 note=other")
    h.append("STATUS lane=lane-1 note=middle")
    h.append("TERMINAL lane=lane-1 outcome=done")
    rows = h.store.rows_for_lane("lane-1")
    assert rows == (
        "CLAIM lane=lane-1 ticket=T1",
        "STATUS lane=lane-1 note=middle",
        "TERMINAL lane=lane-1 outcome=done",
    )
    assert isinstance(rows, tuple)


def check_a_lane_name_that_prefixes_another_does_not_match(h: LedgerHarness) -> None:
    h.append("STATUS lane=lane-10 note=x")
    assert h.store.rows_for_lane("lane-1") == ()


def check_queued_rows_are_scoped_to_the_lane_and_the_run(h: LedgerHarness) -> None:
    h.queue("lane-1", "run-1", "STATUS lane=lane-1 note=q1")
    h.queue("lane-1", "run-1", "STATUS lane=lane-1 note=q2")
    h.queue("lane-1", "run-2", "STATUS lane=lane-1 note=later-run")
    h.queue("lane-2", "run-1", "STATUS lane=lane-2 note=other-lane")
    assert h.store.queued_rows("lane-1", "run-1") == (
        "STATUS lane=lane-1 note=q1",
        "STATUS lane=lane-1 note=q2",
    )
    assert h.store.queued_rows("lane-1", "run-3") == ()


CHECKS: tuple[Callable[[LedgerHarness], None], ...] = (
    check_is_protocol_instance,
    check_a_lane_with_no_rows_gets_an_empty_tuple,
    check_rows_for_lane_are_that_lanes_rows_oldest_first,
    check_a_lane_name_that_prefixes_another_does_not_match,
    check_queued_rows_are_scoped_to_the_lane_and_the_run,
)
