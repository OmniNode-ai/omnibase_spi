# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Checks every ProtocolLaneProcessRunner adapter must pass (OMN-22851).

A real adapter is wrapped in a harness that arranges which outcome the next call
answers; the checks read only what the protocol returns.
"""

from collections.abc import Callable
from typing import Protocol

from omnibase_spi.contracts.services import (
    ModelLaneProcessRunResult,
    ModelLaneProcessStartResult,
    ModelLaneStartSpec,
)
from omnibase_spi.protocols.lane import ProtocolLaneProcessRunner

SPEC = ModelLaneStartSpec(
    argv=("runner", "--lane", "lane-1"),
    environment=(("KEY", "value"),),
    working_directory="/work",
    lane="lane-1",
)


class LaneProcessHarness(Protocol):
    runner: ProtocolLaneProcessRunner

    def arrange_start(self, result: ModelLaneProcessStartResult) -> None: ...

    def arrange_run(self, result: ModelLaneProcessRunResult) -> None: ...


def check_is_protocol_instance(h: LaneProcessHarness) -> None:
    assert isinstance(h.runner, ProtocolLaneProcessRunner)


def check_a_started_process_comes_back_with_its_pid(h: LaneProcessHarness) -> None:
    h.arrange_start(ModelLaneProcessStartResult(state="started", pid=77))
    result = h.runner.start_detached(SPEC)
    assert result.state == "started" and result.pid == 77 and result.cause is None


def check_a_failed_start_is_typed_with_its_cause(h: LaneProcessHarness) -> None:
    h.arrange_start(
        ModelLaneProcessStartResult(state="failed", cause="executable missing")
    )
    result = h.runner.start_detached(SPEC)
    assert result.state == "failed" and result.pid is None
    assert result.cause == "executable missing"


def check_a_run_that_ends_returns_its_exit_code_and_output(
    h: LaneProcessHarness,
) -> None:
    h.arrange_run(ModelLaneProcessRunResult(state="exited", exit_code=3, stdout="out"))
    result = h.runner.run_bounded(SPEC, 5.0)
    assert result.state == "exited" and result.exit_code == 3
    assert result.stdout == "out" and result.cause is None


def check_a_run_past_its_deadline_is_timed_out_and_carries_no_exit_code(
    h: LaneProcessHarness,
) -> None:
    h.arrange_run(ModelLaneProcessRunResult(state="timed_out"))
    result = h.runner.run_bounded(SPEC, 0.5)
    assert result.state == "timed_out" and result.exit_code is None
    assert result.stdout == ""


def check_a_run_that_cannot_happen_is_failed_with_its_cause(
    h: LaneProcessHarness,
) -> None:
    h.arrange_run(ModelLaneProcessRunResult(state="failed", cause="executable missing"))
    result = h.runner.run_bounded(SPEC, 5.0)
    assert result.state == "failed" and result.cause == "executable missing"


CHECKS: tuple[Callable[[LaneProcessHarness], None], ...] = (
    check_is_protocol_instance,
    check_a_started_process_comes_back_with_its_pid,
    check_a_failed_start_is_typed_with_its_cause,
    check_a_run_that_ends_returns_its_exit_code_and_output,
    check_a_run_past_its_deadline_is_timed_out_and_carries_no_exit_code,
    check_a_run_that_cannot_happen_is_failed_with_its_cause,
)
