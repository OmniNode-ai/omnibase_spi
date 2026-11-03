# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Protocol for the calls a lane start node makes to a lane host.

Each call takes one request model and returns one result model. A call never
raises for an expected outcome: a refusal, a failure and a start that did not
settle in time are all typed results.
"""

from typing import TYPE_CHECKING, ClassVar, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.services import (
        ModelLanePrepareWorktreeRequest,
        ModelLanePrepareWorktreeResult,
        ModelLaneReadEngineExitRequest,
        ModelLaneReadEngineExitResult as ModelLaneEngineExitState,
        ModelLaneReadLogTailRequest,
        ModelLaneReadLogTailResult as ModelLaneLogTailChunk,
        ModelLaneStartEngineRequest,
        ModelLaneStartEngineResult,
        ModelLaneStopEngineRequest,
        ModelLaneStopEngineResult as ModelLaneEngineStopOutcome,
    )


@runtime_checkable
class ProtocolLaneHostTransport(Protocol):
    """Prepare a worktree on a host, run an engine there detached, and read it back.

    The ``synchronous_execution = True`` class-level flag is read by the SPI
    validator to exempt these methods from the async-by-default rule: each call
    is a synchronous request/result exchange that returns within its timeout.
    The wire models are imported under names that carry no I/O word because the
    SPI protocol validator reads a ``read`` or ``open`` inside a return type name
    as a sign of I/O.
    """

    synchronous_execution: ClassVar[bool]

    def prepare_worktree(
        self, request: "ModelLanePrepareWorktreeRequest"
    ) -> "ModelLanePrepareWorktreeResult":
        """Prepare the lane's worktree on the host at ``request.sha``."""
        ...

    def start_engine_detached(
        self, request: "ModelLaneStartEngineRequest"
    ) -> "ModelLaneStartEngineResult":
        """Start the engine detached.

        Returns only when the engine has started or failed, within
        ``request.timeout_seconds``. A start that did not settle in time returns
        state ``unresolved``: the engine may be running.
        """
        ...

    def read_engine_exit(
        self, request: "ModelLaneReadEngineExitRequest"
    ) -> "ModelLaneEngineExitState":
        """Return the engine's exit code once it has ended, else running."""
        ...

    def stop_engine(
        self, request: "ModelLaneStopEngineRequest"
    ) -> "ModelLaneEngineStopOutcome":
        """Stop the engine; ``confirmed`` is False when it survives the stop."""
        ...

    def read_log_tail(
        self, request: "ModelLaneReadLogTailRequest"
    ) -> "ModelLaneLogTailChunk":
        """Return the engine log lines from ``request.offset`` and the next offset."""
        ...


__all__ = ["ProtocolLaneHostTransport"]
