# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Wire-format contracts for ProtocolLaneProcessRunner: one spec, two results.

This module MUST NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class ModelLaneStartSpec(BaseModel):
    """What to start: the argv, its environment and working directory, and the lane it is for.

    The adapter owns the log path of a detached start; the spec never names it.

    Attributes:
        argv: The command and its arguments as separate elements.
        environment: Environment variables as name and value pairs.
        working_directory: Directory the process starts in.
        lane: The lane the process is for.
    """

    model_config = _FROZEN

    argv: tuple[str, ...] = Field(
        ..., min_length=1, description="Command and arguments."
    )
    environment: tuple[tuple[str, str], ...] = Field(
        default=(), description="Environment variables as name and value pairs."
    )
    working_directory: str = Field(
        ..., min_length=1, description="Directory the process starts in."
    )
    lane: str = Field(..., min_length=1, description="Lane the process is for.")


class ModelLaneProcessStartResult(BaseModel):
    """Outcome of a detached start.

    Attributes:
        state: ``started`` when the process was started, ``failed`` when it was not.
        pid: Process id of the started process; absent when the start failed.
        cause: Why the start failed; absent when it started.
    """

    model_config = _FROZEN

    state: Literal["started", "failed"] = Field(..., description="Start outcome.")
    pid: int | None = Field(
        default=None, ge=1, description="Pid of the started process."
    )
    cause: str | None = Field(default=None, description="Why the start failed.")

    @model_validator(mode="after")
    def _shape_follows_state(self) -> Self:
        if self.state == "started":
            if self.pid is None or self.cause is not None:
                raise ValueError("started requires a pid and no cause")
        elif self.cause is None or self.pid is not None:
            raise ValueError("failed requires a cause and no pid")
        return self


class ModelLaneProcessRunResult(BaseModel):
    """Outcome of a command run in the foreground under a deadline.

    Attributes:
        state: ``exited`` when the command ended in time, ``timed_out`` when the
            deadline passed and the child was ended, ``failed`` when it could not be run.
        exit_code: The child's exit code; present only for ``exited``.
        stdout: The child's standard output; empty unless ``exited``.
        cause: Why the command could not be run; present only for ``failed``.
    """

    model_config = _FROZEN

    state: Literal["exited", "timed_out", "failed"] = Field(
        ..., description="Run outcome."
    )
    exit_code: int | None = Field(default=None, description="Exit code when exited.")
    stdout: str = Field(default="", description="Standard output when exited.")
    cause: str | None = Field(default=None, description="Why the run failed.")

    @model_validator(mode="after")
    def _shape_follows_state(self) -> Self:
        if self.state == "exited":
            if self.exit_code is None or self.cause is not None:
                raise ValueError("exited requires an exit_code and no cause")
        elif self.state == "timed_out":
            if self.exit_code is not None or self.cause is not None or self.stdout:
                raise ValueError("timed_out carries no exit_code, stdout or cause")
        elif self.cause is None or self.exit_code is not None or self.stdout:
            raise ValueError("failed requires a cause and no exit_code or stdout")
        return self


__all__ = [
    "ModelLaneProcessRunResult",
    "ModelLaneProcessStartResult",
    "ModelLaneStartSpec",
]
