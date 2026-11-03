# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Checks every ProtocolLaneHostTransport adapter must pass (OMN-22198).

A real adapter is wrapped in a harness that scripts what the host does: how a
start settles, when an engine ends, whether it survives a stop, what it logs.
"""

from collections.abc import Callable, Sequence
from typing import Protocol

from omnibase_spi.contracts.services import (
    ModelLaneHostRef,
    ModelLanePrepareWorktreeRequest,
    ModelLaneReadEngineExitRequest,
    ModelLaneReadLogTailRequest,
    ModelLaneStartEngineRequest,
    ModelLaneStopEngineRequest,
)
from omnibase_spi.protocols.lane import ProtocolLaneHostTransport

HOST = ModelLaneHostRef(name="host-a", target="host-a.example", local=False)
SHA = "0123456789abcdef0123456789abcdef01234567"


class LaneHostHarness(Protocol):
    transport: ProtocolLaneHostTransport

    def script_start(self, state: str) -> None: ...

    def script_prepare_refusal(self, error: str | None) -> None: ...

    def script_exit(self, run_id: str, exit_code: int) -> None: ...

    def script_stubborn(self, run_id: str) -> None: ...

    def script_log(self, run_id: str, lines: Sequence[str]) -> None: ...


def _start(run_id: str) -> ModelLaneStartEngineRequest:
    return ModelLaneStartEngineRequest(
        host=HOST,
        lane="lane-1",
        run_id=run_id,
        workdir="/work",
        engine_argv=("engine", "--go"),
        environment=(("KEY", "value"),),
        timeout_seconds=5.0,
    )


def check_is_protocol_instance(h: LaneHostHarness) -> None:
    assert isinstance(h.transport, ProtocolLaneHostTransport)


def check_prepare_worktree_returns_a_workdir(h: LaneHostHarness) -> None:
    result = h.transport.prepare_worktree(
        ModelLanePrepareWorktreeRequest(
            host=HOST,
            lane="lane-1",
            run_id="run-1",
            repo="omnimarket",
            owner="OmniNode-ai",
            sha=SHA,
            registry_root_candidates=("/omni",),
            timeout_seconds=30.0,
        )
    )
    assert result.prepared is True
    assert result.workdir and result.error is None


def check_a_refused_prepare_is_a_result_with_an_error_not_a_raise(
    h: LaneHostHarness,
) -> None:
    h.script_prepare_refusal("disk full")
    result = h.transport.prepare_worktree(
        ModelLanePrepareWorktreeRequest(
            host=HOST,
            lane="lane-1",
            run_id="run-1",
            repo="omnimarket",
            owner="OmniNode-ai",
            sha=SHA,
            timeout_seconds=30.0,
        )
    )
    assert result.prepared is False
    assert result.error == "disk full" and result.workdir is None


def check_a_started_engine_has_a_session_and_is_running(h: LaneHostHarness) -> None:
    started = h.transport.start_engine_detached(_start("run-2"))
    assert started.state == "started"
    assert started.session_id and started.error is None
    exit_read = h.transport.read_engine_exit(
        ModelLaneReadEngineExitRequest(host=HOST, run_id="run-2")
    )
    assert exit_read.running is True and exit_read.exit_code is None


def check_a_failed_start_names_its_error_and_does_not_raise(
    h: LaneHostHarness,
) -> None:
    h.script_start("failed")
    result = h.transport.start_engine_detached(_start("run-3"))
    assert result.state == "failed" and result.error
    assert result.session_id is None


def check_a_start_that_did_not_settle_is_unresolved_not_failed(
    h: LaneHostHarness,
) -> None:
    h.script_start("unresolved")
    result = h.transport.start_engine_detached(_start("run-4"))
    assert result.state == "unresolved"
    assert result.session_id is None and result.error is None


def check_an_ended_engine_reports_its_exit_code(h: LaneHostHarness) -> None:
    h.transport.start_engine_detached(_start("run-5"))
    h.script_exit("run-5", 3)
    result = h.transport.read_engine_exit(
        ModelLaneReadEngineExitRequest(host=HOST, run_id="run-5")
    )
    assert result.running is False and result.exit_code == 3


def check_stop_confirms_when_the_engine_ended(h: LaneHostHarness) -> None:
    h.transport.start_engine_detached(_start("run-6"))
    result = h.transport.stop_engine(
        ModelLaneStopEngineRequest(host=HOST, run_id="run-6", grace_seconds=1.0)
    )
    assert result.confirmed is True
    after = h.transport.read_engine_exit(
        ModelLaneReadEngineExitRequest(host=HOST, run_id="run-6")
    )
    assert after.running is False


def check_an_engine_that_survives_the_stop_is_not_confirmed(h: LaneHostHarness) -> None:
    h.transport.start_engine_detached(_start("run-7"))
    h.script_stubborn("run-7")
    result = h.transport.stop_engine(
        ModelLaneStopEngineRequest(host=HOST, run_id="run-7", grace_seconds=1.0)
    )
    assert result.confirmed is False
    after = h.transport.read_engine_exit(
        ModelLaneReadEngineExitRequest(host=HOST, run_id="run-7")
    )
    assert after.running is True


def check_log_tail_resumes_from_the_next_offset(h: LaneHostHarness) -> None:
    h.script_log("run-8", ["a", "b", "c"])
    first = h.transport.read_log_tail(
        ModelLaneReadLogTailRequest(host=HOST, run_id="run-8", offset=0)
    )
    assert first.lines == ("a", "b", "c") and first.next_offset == 3
    h.script_log("run-8", ["a", "b", "c", "d"])
    second = h.transport.read_log_tail(
        ModelLaneReadLogTailRequest(host=HOST, run_id="run-8", offset=first.next_offset)
    )
    assert second.lines == ("d",) and second.next_offset == 4
    again = h.transport.read_log_tail(
        ModelLaneReadLogTailRequest(host=HOST, run_id="run-8", offset=4)
    )
    assert again.lines == () and again.next_offset == 4


CHECKS: tuple[Callable[[LaneHostHarness], None], ...] = (
    check_is_protocol_instance,
    check_prepare_worktree_returns_a_workdir,
    check_a_refused_prepare_is_a_result_with_an_error_not_a_raise,
    check_a_started_engine_has_a_session_and_is_running,
    check_a_failed_start_names_its_error_and_does_not_raise,
    check_a_start_that_did_not_settle_is_unresolved_not_failed,
    check_an_ended_engine_reports_its_exit_code,
    check_stop_confirms_when_the_engine_ended,
    check_an_engine_that_survives_the_stop_is_not_confirmed,
    check_log_tail_resumes_from_the_next_offset,
)
