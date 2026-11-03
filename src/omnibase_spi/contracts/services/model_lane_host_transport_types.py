# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Wire-format contracts for ProtocolLaneHostTransport: one request and one result per call.

Every call returns a typed result for an expected outcome; none raises for one.
This module MUST NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class ModelLaneHostRef(BaseModel):
    """The host a transport call is aimed at.

    Attributes:
        name: Host name as the host pool knows it.
        target: How to reach the host (an address or ssh target); None for none.
        local: True when the host is the machine the caller runs on.
    """

    model_config = _FROZEN

    name: str = Field(..., min_length=1, description="Host name.")
    target: str | None = Field(default=None, description="Address or ssh target.")
    local: bool = Field(default=False, description="True for the caller's own machine.")


class ModelLanePrepareWorktreeRequest(BaseModel):
    """Ask a host to prepare the lane's worktree at an exact sha.

    Attributes:
        host: The host to prepare on.
        lane: Lane name.
        run_id: Run id of this lane run.
        repo: Repository name.
        owner: Repository owner.
        sha: The 40-character commit sha the worktree must sit at.
        registry_root_candidates: Paths the host may use as its registry_root, in order.
        timeout_seconds: Longest the call may take.
    """

    model_config = _FROZEN

    host: ModelLaneHostRef = Field(..., description="Host to prepare on.")
    lane: str = Field(..., description="Lane name.")
    run_id: str = Field(..., description="Run id of this lane run.")
    repo: str = Field(..., description="Repository name.")
    owner: str = Field(..., description="Repository owner.")
    sha: str = Field(
        ..., pattern=r"^[0-9a-f]{40}$", description="Commit sha, 40 lowercase hex."
    )
    registry_root_candidates: tuple[str, ...] = Field(
        default=(), description="Candidate registry_root paths, in order."
    )
    timeout_seconds: float = Field(..., gt=0, description="Longest the call may take.")


class ModelLanePrepareWorktreeResult(BaseModel):
    """Outcome of preparing a worktree.

    Attributes:
        prepared: True when the worktree is ready at the requested sha.
        registry_root: The registry_root path the host used.
        workdir: The prepared worktree path; required when prepared.
        error: Why preparing failed; required when not prepared.
    """

    model_config = _FROZEN

    prepared: bool = Field(..., description="True when the worktree is ready.")
    registry_root: str | None = Field(
        default=None, description="registry_root the host used."
    )
    workdir: str | None = Field(default=None, description="Prepared worktree path.")
    error: str | None = Field(default=None, description="Why preparing failed.")

    @model_validator(mode="after")
    def _fields_match_prepared(self) -> Self:
        if self.prepared and not self.workdir:
            raise ValueError("a prepared worktree names its workdir")
        if not self.prepared and not self.error:
            raise ValueError("a worktree that was not prepared names its error")
        return self


class ModelLaneStartEngineRequest(BaseModel):
    """Ask a host to start an engine detached in a prepared worktree.

    Attributes:
        host: The host to start on.
        lane: Lane name.
        run_id: Run id of this lane run.
        workdir: The prepared worktree path.
        engine_argv: The engine command line; at least one element.
        environment: Environment as (name, value) pairs.
        timeout_seconds: Longest to wait for the engine to start or fail.
    """

    model_config = _FROZEN

    host: ModelLaneHostRef = Field(..., description="Host to start on.")
    lane: str = Field(..., description="Lane name.")
    run_id: str = Field(..., description="Run id of this lane run.")
    workdir: str = Field(..., description="Prepared worktree path.")
    engine_argv: tuple[str, ...] = Field(
        ..., min_length=1, description="Engine command line."
    )
    environment: tuple[tuple[str, str], ...] = Field(
        default=(), description="Environment as (name, value) pairs."
    )
    timeout_seconds: float = Field(
        ..., gt=0, description="Longest to wait for the engine to start or fail."
    )


class ModelLaneStartEngineResult(BaseModel):
    """Outcome of starting an engine.

    Attributes:
        state: ``started``, ``failed`` or ``unresolved``. ``unresolved`` means
            the start did not settle in time and the engine may be running.
        session_id: The engine session; required for ``started``.
        error: Why the start failed; required for ``failed``.
    """

    model_config = _FROZEN

    state: Literal["started", "failed", "unresolved"] = Field(
        ..., description="started, failed or unresolved."
    )
    session_id: str | None = Field(default=None, description="Engine session id.")
    error: str | None = Field(default=None, description="Why the start failed.")

    @model_validator(mode="after")
    def _fields_match_state(self) -> Self:
        if self.state == "started":
            if not self.session_id:
                raise ValueError("a started engine names its session_id")
            if self.error is not None:
                raise ValueError("a started engine carries no error")
        elif self.state == "failed" and not self.error:
            raise ValueError("a failed start names its error")
        return self


class ModelLaneReadEngineExitRequest(BaseModel):
    """Ask a host whether the run's engine has ended.

    Attributes:
        host: The host the engine runs on.
        run_id: Run id of this lane run.
    """

    model_config = _FROZEN

    host: ModelLaneHostRef = Field(..., description="Host the engine runs on.")
    run_id: str = Field(..., description="Run id of this lane run.")


class ModelLaneReadEngineExitResult(BaseModel):
    """Whether the engine is still running or has ended with an exit code.

    Attributes:
        running: True while the engine has not ended.
        exit_code: The exit code once ended; absent while running.
    """

    model_config = _FROZEN

    running: bool = Field(..., description="True while the engine has not ended.")
    exit_code: int | None = Field(default=None, description="Exit code once ended.")

    @model_validator(mode="after")
    def _running_xor_exit_code(self) -> Self:
        if self.running == (self.exit_code is not None):
            raise ValueError("exactly one of running and exit_code is present")
        return self


class ModelLaneStopEngineRequest(BaseModel):
    """Ask a host to stop the run's engine.

    Attributes:
        host: The host the engine runs on.
        run_id: Run id of this lane run.
        grace_seconds: How long the engine gets before it is killed.
    """

    model_config = _FROZEN

    host: ModelLaneHostRef = Field(..., description="Host the engine runs on.")
    run_id: str = Field(..., description="Run id of this lane run.")
    grace_seconds: float = Field(..., gt=0, description="Grace before the kill.")


class ModelLaneStopEngineResult(BaseModel):
    """Outcome of stopping an engine.

    Attributes:
        confirmed: True when the engine has ended; False when it survived the stop.
        exit_code: The exit code, when known.
        detail: Free-text detail for the log.
    """

    model_config = _FROZEN

    confirmed: bool = Field(..., description="True when the engine has ended.")
    exit_code: int | None = Field(default=None, description="Exit code, when known.")
    detail: str = Field(default="", description="Detail for the log.")


class ModelLaneReadLogTailRequest(BaseModel):
    """Ask a host for the engine log from an offset.

    Attributes:
        host: The host the engine runs on.
        run_id: Run id of this lane run.
        offset: Line offset to read from.
    """

    model_config = _FROZEN

    host: ModelLaneHostRef = Field(..., description="Host the engine runs on.")
    run_id: str = Field(..., description="Run id of this lane run.")
    offset: int = Field(..., ge=0, description="Line offset to read from.")


class ModelLaneReadLogTailResult(BaseModel):
    """Log lines from an offset and the offset to read next.

    Attributes:
        lines: The lines read.
        next_offset: Offset to pass on the next read.
    """

    model_config = _FROZEN

    lines: tuple[str, ...] = Field(default=(), description="Lines read.")
    next_offset: int = Field(..., ge=0, description="Offset for the next read.")


__all__ = [
    "ModelLaneHostRef",
    "ModelLanePrepareWorktreeRequest",
    "ModelLanePrepareWorktreeResult",
    "ModelLaneReadEngineExitRequest",
    "ModelLaneReadEngineExitResult",
    "ModelLaneReadLogTailRequest",
    "ModelLaneReadLogTailResult",
    "ModelLaneStartEngineRequest",
    "ModelLaneStartEngineResult",
    "ModelLaneStopEngineRequest",
    "ModelLaneStopEngineResult",
]
