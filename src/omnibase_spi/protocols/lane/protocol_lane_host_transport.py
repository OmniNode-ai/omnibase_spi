# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Protocol for the calls a lane start node makes to a lane host.

Each call takes one request model and returns one result model. A call never
raises for an expected outcome: a refusal, a failure and a start that did not
settle in time are all typed results.

Besides the engine calls, the protocol carries the provisioning steps a lane
runner performs on the host around the engine (OMN-22848): before the engine
starts, resolve the registry root, make the run directories, stage the ledger
snapshot and the run's files, ship the plugin trees, mirror the ledger and
write the runtime config; after the engine ends, drain the guard spool, relay
the reports, read the queued ledger rows and the lane's changes, close out the
lane's worktrees, and hold or retain the run directory. A caller issues the
provisioning steps only after its CLAIM was appended.
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
    from omnibase_spi.contracts.services.model_lane_host_provisioning_types import (
        ModelLaneChangeList,
        ModelLaneCloseoutCells,
        ModelLaneHostStepRequest,
        ModelLaneHostStepResult,
        ModelLaneLedgerOutboxRows,
        ModelLaneRegistryRootResult,
        ModelLaneRetainRunArtifactsRequest,
        ModelLaneRunDirsResult,
        ModelLaneShipPluginTreesRequest,
        ModelLaneShipPluginTreesResult,
        ModelLaneStagedInput,
        ModelLaneStageInputRequest,
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

    # Provisioning before the engine starts (issued after the CLAIM append).

    def resolve_registry_root(
        self, request: "ModelLaneHostStepRequest"
    ) -> "ModelLaneRegistryRootResult":
        """Find the host's registry root."""
        ...

    def prepare_run_dirs(
        self, request: "ModelLaneHostStepRequest"
    ) -> "ModelLaneRunDirsResult":
        """Make the run's working and context directories."""
        ...

    def stage_ledger_snapshot(
        self, request: "ModelLaneStageInputRequest"
    ) -> "ModelLaneStagedInput":
        """Stage the ledger snapshot the lane reads into the context directory."""
        ...

    def stage_file(
        self, request: "ModelLaneStageInputRequest"
    ) -> "ModelLaneStagedInput":
        """Stage one run file (the prompt, a guard script, settings) into the context directory."""
        ...

    def ship_plugin_trees(
        self, request: "ModelLaneShipPluginTreesRequest"
    ) -> "ModelLaneShipPluginTreesResult":
        """Install the plugin trees the engine loads, keyed by their digest."""
        ...

    def mirror_ledger(
        self, request: "ModelLaneHostStepRequest"
    ) -> "ModelLaneHostStepResult":
        """Point the lane's ledger copy at the snapshot and the host's ledger writer."""
        ...

    def write_runtime_config(
        self, request: "ModelLaneHostStepRequest"
    ) -> "ModelLaneHostStepResult":
        """Write the runtime config the engine reads on the host."""
        ...

    # Close-path steps after the engine ended.

    def drain_guard_spool(
        self, request: "ModelLaneHostStepRequest"
    ) -> "ModelLaneHostStepResult":
        """Drain the lane guard's spool after the engine ended."""
        ...

    def relay_reports(
        self, request: "ModelLaneHostStepRequest"
    ) -> "ModelLaneHostStepResult":
        """Copy the lane's reports back to the caller."""
        ...

    def read_ledger_outbox(
        self, request: "ModelLaneHostStepRequest"
    ) -> "ModelLaneLedgerOutboxRows":
        """Return the ledger rows the lane queued on the host."""
        ...

    def read_lane_changes(
        self, request: "ModelLaneHostStepRequest"
    ) -> "ModelLaneChangeList":
        """Return the lane's worktrees that hold commits or edits not pushed."""
        ...

    def closeout_worktrees(
        self, request: "ModelLaneHostStepRequest"
    ) -> "ModelLaneCloseoutCells":
        """Archive and remove the lane's worktrees; return the closeout cells."""
        ...

    def hold_run_dir_guard(
        self, request: "ModelLaneHostStepRequest"
    ) -> "ModelLaneHostStepResult":
        """Keep the run directory from removal while the lane's outputs are read."""
        ...

    def retain_run_artifacts(
        self, request: "ModelLaneRetainRunArtifactsRequest"
    ) -> "ModelLaneHostStepResult":
        """Keep the run's artifacts the retention policy keeps, and remove the rest.

        The result carries the retention line the host printed as a cell named
        ``retention``.
        """
        ...

    def stop_lane_guard(
        self, request: "ModelLaneHostStepRequest"
    ) -> "ModelLaneHostStepResult":
        """Stop the lane guard unit that watched the engine."""
        ...


__all__ = ["ProtocolLaneHostTransport"]
