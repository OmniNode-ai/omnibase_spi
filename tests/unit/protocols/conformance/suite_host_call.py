# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Checks every ProtocolHostCall adapter must pass.

A real adapter is wrapped in a harness that arranges what the host does for an
operation: answer ok, refuse with a cause, or not answer within the timeout.
"""

from collections.abc import Callable
from typing import Protocol

from omnibase_spi.contracts.services import ModelHostCallRequest
from omnibase_spi.protocols.runtime import ProtocolHostCall


class HostCallHarness(Protocol):
    host: ProtocolHostCall

    def arrange_ok(self, operation: str, fields: dict[str, str]) -> None: ...

    def arrange_refused(self, operation: str, cause: str) -> None: ...

    def arrange_silence(self, operation: str) -> None: ...


def check_is_protocol_instance(h: HostCallHarness) -> None:
    assert isinstance(h.host, ProtocolHostCall)


def check_ok_answer_repeats_the_request_id_and_carries_fields(
    h: HostCallHarness,
) -> None:
    h.arrange_ok("status", {"permit": "done"})
    answer = h.host.call(
        ModelHostCallRequest(request_id="r1", operation="status"), timeout_s=1.0
    )
    assert answer.request_id == "r1"
    assert answer.outcome == "ok" and answer.cause is None
    assert answer.fields == {"permit": "done"}


def check_refused_answer_names_its_cause(h: HostCallHarness) -> None:
    h.arrange_refused("offer", "session-running")
    answer = h.host.call(
        ModelHostCallRequest(request_id="r2", operation="offer"), timeout_s=1.0
    )
    assert answer.request_id == "r2"
    assert answer.outcome == "refused" and answer.cause == "session-running"


def check_no_answer_in_time_is_unknown_and_does_not_raise(h: HostCallHarness) -> None:
    h.arrange_silence("cancel")
    answer = h.host.call(
        ModelHostCallRequest(request_id="r3", operation="cancel"), timeout_s=0.05
    )
    assert answer.request_id == "r3"
    assert answer.outcome == "unknown" and answer.cause is None


CHECKS: tuple[Callable[[HostCallHarness], None], ...] = (
    check_is_protocol_instance,
    check_ok_answer_repeats_the_request_id_and_carries_fields,
    check_refused_answer_names_its_cause,
    check_no_answer_in_time_is_unknown_and_does_not_raise,
)
