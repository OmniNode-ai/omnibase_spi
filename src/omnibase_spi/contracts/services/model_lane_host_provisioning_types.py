# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Wire-format contracts for the provisioning calls of ProtocolLaneHostTransport.

A lane runner provisions a host around the engine: it finds the registry root,
makes the run directories, stages the ledger snapshot, the prompt and other
files, ships the plugin trees and writes the runtime config before the engine
starts, and after the engine ends it drains the guard spool, relays reports,
reads the queued ledger rows and the lane's changes, closes out its worktrees
and retains or removes the run directory. Each of those steps is one call here,
with a typed request and a typed result; none raises for an expected outcome.
This module MUST NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from omnibase_spi.contracts.services.model_lane_host_transport_types import (
    ModelLaneHostRef,
)

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class ModelLaneHostStepRequest(BaseModel):
    """One provisioning step of a lane run on a host.

    Attributes:
        host: Host the step runs on.
        lane: Lane name.
        run_id: Run id of this lane run.
        registry_root: The host's registry root once resolved; None before.
        timeout_seconds: Longest the call may take.
    """

    model_config = _FROZEN

    host: ModelLaneHostRef = Field(..., description="Host the step runs on.")
    lane: str = Field(..., min_length=1, description="Lane name.")
    run_id: str = Field(..., min_length=1, description="Run id of this lane run.")
    registry_root: str | None = Field(
        default=None, description="Registry root on the host, once resolved."
    )
    timeout_seconds: float = Field(..., gt=0, description="Longest the call may take.")


class ModelLaneHostStepResult(BaseModel):
    """What one provisioning step did.

    Attributes:
        ok: True when the step did what it was asked.
        cells: Named facts the step reports, in its own order.
        detail: Detail for the log.
        error: Why the step failed; required when ``ok`` is False.
    """

    model_config = _FROZEN

    ok: bool = Field(..., description="True when the step did what it was asked.")
    cells: tuple[tuple[str, str], ...] = Field(
        default=(), description="Named facts the step reports."
    )
    detail: str = Field(default="", description="Detail for the log.")
    error: str | None = Field(default=None, description="Why the step failed.")

    @model_validator(mode="after")
    def _failure_names_its_error(self) -> Self:
        if not self.ok and not self.error:
            raise ValueError("a failed step names its error")
        return self


class ModelLaneRegistryRootResult(BaseModel):
    """The registry root found on the host.

    Attributes:
        registry_root: The root path; None when none was found.
        error: Why none was found; required when ``registry_root`` is None.
    """

    model_config = _FROZEN

    registry_root: str | None = Field(default=None, description="Registry root path.")
    error: str | None = Field(default=None, description="Why no root was found.")

    @model_validator(mode="after")
    def _missing_root_names_its_error(self) -> Self:
        if self.registry_root is None and not self.error:
            raise ValueError("a missing registry root names its error")
        return self


class ModelLaneRunDirsResult(BaseModel):
    """The run directories made for the lane run.

    Attributes:
        run_dir: Working directory of the run.
        context_dir: Directory the staged files go to.
        error: Why the directories were not made.
    """

    model_config = _FROZEN

    run_dir: str | None = Field(
        default=None, description="Working directory of the run."
    )
    context_dir: str | None = Field(
        default=None, description="Directory the staged files go to."
    )
    error: str | None = Field(
        default=None, description="Why the directories were not made."
    )

    @model_validator(mode="after")
    def _dirs_or_error(self) -> Self:
        if (self.run_dir is None or self.context_dir is None) and not self.error:
            raise ValueError("run directories not made name their error")
        return self


class ModelLaneStageInputRequest(BaseModel):
    """A file to stage into the run's context directory on the host.

    Attributes:
        host: Host to stage on.
        lane: Lane name.
        run_id: Run id of this lane run.
        name: File name inside the context directory; no path separator.
        content: File content.
        mode: File mode bits.
        timeout_seconds: Longest the call may take.
    """

    model_config = _FROZEN

    host: ModelLaneHostRef = Field(..., description="Host to stage on.")
    lane: str = Field(..., min_length=1, description="Lane name.")
    run_id: str = Field(..., min_length=1, description="Run id of this lane run.")
    name: str = Field(
        ..., min_length=1, pattern=r"^[^/\\]+$", description="File name, no separator."
    )
    content: str = Field(..., description="File content.")
    mode: int = Field(default=0o600, ge=0, le=0o777, description="File mode bits.")
    timeout_seconds: float = Field(..., gt=0, description="Longest the call may take.")


class ModelLaneStagedInput(BaseModel):
    """Where the staged file landed.

    Attributes:
        staged: True when the file is in place.
        path: The file's path on the host.
        error: Why the file was not staged.
    """

    model_config = _FROZEN

    staged: bool = Field(..., description="True when the file is in place.")
    path: str | None = Field(default=None, description="File path on the host.")
    error: str | None = Field(default=None, description="Why the file was not staged.")

    @model_validator(mode="after")
    def _fields_match_staged(self) -> Self:
        if self.staged and not self.path:
            raise ValueError("a staged file names its path")
        if not self.staged and not self.error:
            raise ValueError("a file that was not staged names its error")
        return self


class ModelLanePluginTree(BaseModel):
    """One plugin tree to ship to the host.

    Attributes:
        name: Plugin name as the engine loads it.
        source_digest: Digest of the tree's content, naming the installed copy.
        archive_path: Path of the tree's archive on the caller's machine.
    """

    model_config = _FROZEN

    name: str = Field(..., min_length=1, description="Plugin name.")
    source_digest: str = Field(..., min_length=1, description="Digest of the tree.")
    archive_path: str = Field(
        ..., min_length=1, description="Archive path on the caller."
    )


class ModelLaneShipPluginTreesRequest(BaseModel):
    """The plugin trees the engine on the host loads.

    Attributes:
        host: Host to ship to.
        lane: Lane name.
        run_id: Run id of this lane run.
        trees: The trees, in load order.
        timeout_seconds: Longest the call may take.
    """

    model_config = _FROZEN

    host: ModelLaneHostRef = Field(..., description="Host to ship to.")
    lane: str = Field(..., min_length=1, description="Lane name.")
    run_id: str = Field(..., min_length=1, description="Run id of this lane run.")
    trees: tuple[ModelLanePluginTree, ...] = Field(
        default=(), description="Plugin trees in load order."
    )
    timeout_seconds: float = Field(..., gt=0, description="Longest the call may take.")


class ModelLaneShipPluginTreesResult(BaseModel):
    """Where each shipped plugin tree sits on the host.

    Attributes:
        shipped: True when every tree is in place.
        plugin_dirs: ``(name, directory)`` per shipped tree.
        error: Why a tree was not shipped.
    """

    model_config = _FROZEN

    shipped: bool = Field(..., description="True when every tree is in place.")
    plugin_dirs: tuple[tuple[str, str], ...] = Field(
        default=(), description="(name, directory) per shipped tree."
    )
    error: str | None = Field(default=None, description="Why a tree was not shipped.")

    @model_validator(mode="after")
    def _failure_names_its_error(self) -> Self:
        if not self.shipped and not self.error:
            raise ValueError("trees that were not shipped name their error")
        return self


class ModelLaneLedgerOutboxRows(BaseModel):
    """The ledger rows the lane queued on the host because it could not write them.

    Attributes:
        rows: Queued rows, oldest first.
        error: Why the outbox could not be read; None when it was.
    """

    model_config = _FROZEN

    rows: tuple[str, ...] = Field(default=(), description="Queued rows, oldest first.")
    error: str | None = Field(default=None, description="Why the outbox was not read.")


class ModelLaneChangeList(BaseModel):
    """The lane's changes on the host: worktrees with commits or edits not pushed.

    Attributes:
        changes: One line per changed worktree.
        error: Why the changes could not be read; None when they were.
    """

    model_config = _FROZEN

    changes: tuple[str, ...] = Field(
        default=(), description="One line per changed worktree."
    )
    error: str | None = Field(
        default=None, description="Why the changes were not read."
    )


class ModelLaneCloseoutCells(BaseModel):
    """The closeout of the lane's worktrees on the host.

    Attributes:
        cells: Ledger cells the closeout gives, such as ``worktree=removed:<path>``.
        unavailable: True when the host has no closeout tool.
        error: Why the closeout failed; None when it ran.
    """

    model_config = _FROZEN

    cells: tuple[str, ...] = Field(
        default=(), description="Ledger cells of the closeout."
    )
    unavailable: bool = Field(default=False, description="True when no closeout tool.")
    error: str | None = Field(default=None, description="Why the closeout failed.")


__all__ = [
    "ModelLaneChangeList",
    "ModelLaneCloseoutCells",
    "ModelLaneHostStepRequest",
    "ModelLaneHostStepResult",
    "ModelLaneLedgerOutboxRows",
    "ModelLanePluginTree",
    "ModelLaneRegistryRootResult",
    "ModelLaneRunDirsResult",
    "ModelLaneShipPluginTreesRequest",
    "ModelLaneShipPluginTreesResult",
    "ModelLaneStageInputRequest",
    "ModelLaneStagedInput",
]
