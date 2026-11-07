# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for starting a lane runner and running a bounded command on the fill host."""

from typing import TYPE_CHECKING, ClassVar, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.services import (
        ModelLaneProcessRunResult,
        ModelLaneProcessStartResult,
        ModelLaneStartSpec,
    )


@runtime_checkable
class ProtocolLaneProcessRunner(Protocol):
    """Start a lane runner detached, or run one command in the foreground under a deadline.

    Neither call raises for an expected outcome: a start or a run that cannot happen
    is a typed ``failed`` result with its cause. The ``synchronous_execution = True``
    class-level flag is read by the SPI validator to exempt both methods from the
    async-by-default rule: each call is a synchronous spec/result exchange.
    """

    synchronous_execution: ClassVar[bool]

    def start_detached(
        self, spec: "ModelLaneStartSpec"
    ) -> "ModelLaneProcessStartResult":
        """Start ``spec.argv`` in a session of its own and return at once with its pid.

        The adapter holds no handle on the started process, signals nothing and
        waits for nothing; the process's output goes to a log the adapter names.
        """
        ...

    def run_bounded(
        self, spec: "ModelLaneStartSpec", timeout_seconds: float
    ) -> "ModelLaneProcessRunResult":
        """Run ``spec.argv`` to its end or to ``timeout_seconds``, whichever comes first.

        At the deadline the local child is ended and no child is left running.
        """
        ...


__all__ = ["ProtocolLaneProcessRunner"]
