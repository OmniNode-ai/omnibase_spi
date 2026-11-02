# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Checks every ProtocolContainmentUnit adapter must pass.

A real adapter is wrapped in a harness that supplies a long-running command and
can start a member that detaches from the unit's main process.
"""

from collections.abc import Callable, Sequence
from typing import Protocol

from omnibase_spi.exceptions import InvalidProtocolStateError
from omnibase_spi.protocols.runtime import ProtocolContainmentUnit


class ContainmentHarness(Protocol):
    unit: ProtocolContainmentUnit
    long_running_argv: Sequence[str]

    def add_detached_member(self, unit: str) -> int:
        """Start a process in ``unit`` that is not the main command; return its pid."""
        ...


def check_is_protocol_instance(h: ContainmentHarness) -> None:
    assert isinstance(h.unit, ProtocolContainmentUnit)


def check_run_contained_puts_the_command_in_the_unit(h: ContainmentHarness) -> None:
    pid = h.unit.run_contained("u-run", h.long_running_argv)
    try:
        assert pid in h.unit.members("u-run")
    finally:
        assert h.unit.stop("u-run", 10.0) is True


def check_a_busy_unit_refuses_a_second_command(h: ContainmentHarness) -> None:
    h.unit.run_contained("u-busy", h.long_running_argv)
    try:
        try:
            h.unit.run_contained("u-busy", h.long_running_argv)
        except InvalidProtocolStateError:
            return
        raise AssertionError("a busy unit accepted a second command")
    finally:
        assert h.unit.stop("u-busy", 10.0) is True


def check_an_unknown_unit_has_no_members(h: ContainmentHarness) -> None:
    assert h.unit.members("u-unknown") == ()
    assert h.unit.stop("u-unknown", 1.0) is True


def check_stop_kills_every_member_and_confirms_empty(h: ContainmentHarness) -> None:
    main = h.unit.run_contained("u-stop", h.long_running_argv)
    detached = h.add_detached_member("u-stop")
    assert {main, detached} <= set(h.unit.members("u-stop"))
    assert h.unit.stop("u-stop", 10.0) is True
    assert h.unit.members("u-stop") == ()


def check_a_stopped_unit_can_run_again(h: ContainmentHarness) -> None:
    h.unit.run_contained("u-again", h.long_running_argv)
    assert h.unit.stop("u-again", 10.0) is True
    pid = h.unit.run_contained("u-again", h.long_running_argv)
    try:
        assert pid in h.unit.members("u-again")
    finally:
        assert h.unit.stop("u-again", 10.0) is True


CHECKS: tuple[Callable[[ContainmentHarness], None], ...] = (
    check_is_protocol_instance,
    check_run_contained_puts_the_command_in_the_unit,
    check_a_busy_unit_refuses_a_second_command,
    check_an_unknown_unit_has_no_members,
    check_stop_kills_every_member_and_confirms_empty,
    check_a_stopped_unit_can_run_again,
)
