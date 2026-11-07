# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""In-memory adapters for the five lander protocols (OMN-22185) and the three lane protocols (OMN-22198) and the lane process runner (OMN-22851).

They live with the conformance suites, not in the package: the omnibase_spi purity
gate allows no concrete class in ``src``. Each is the ``local``-profile adapter of
its protocol and passes the same checks as any real adapter.
"""

import itertools
import threading
from collections.abc import Callable, Sequence

from omnibase_spi.contracts.services import (
    ModelHostCallAnswer,
    ModelHostCallRequest,
    ModelLaneChangeList,
    ModelLaneCloseoutCells,
    ModelLaneHostPoolRequest,
    ModelLaneHostPoolSnapshot,
    ModelLaneHostStepRequest,
    ModelLaneHostStepResult,
    ModelLaneLedgerOutboxRows,
    ModelLanePrepareWorktreeRequest,
    ModelLanePrepareWorktreeResult,
    ModelLaneProcessRunResult,
    ModelLaneProcessStartResult,
    ModelLaneReadEngineExitRequest,
    ModelLaneReadEngineExitResult,
    ModelLaneReadLogTailRequest,
    ModelLaneReadLogTailResult,
    ModelLaneRegistryRootResult,
    ModelLaneRunDirsResult,
    ModelLaneShipPluginTreesRequest,
    ModelLaneShipPluginTreesResult,
    ModelLaneStagedInput,
    ModelLaneStageInputRequest,
    ModelLaneStartEngineRequest,
    ModelLaneStartEngineResult,
    ModelLaneStartSpec,
    ModelLaneStopEngineRequest,
    ModelLaneStopEngineResult,
)
from omnibase_spi.contracts.source_control import ModelPushResult
from omnibase_spi.exceptions import InvalidProtocolStateError


class InMemoryDurableStore:
    """A durable store that keeps its entries in a dict behind one lock."""

    def __init__(self) -> None:
        self._entries: dict[str, bytes] = {}
        self._lock = threading.Lock()

    async def read(self, path: str) -> bytes | None:
        """Return the entry's bytes, or None when the entry does not exist."""
        with self._lock:
            return self._entries.get(path)

    async def write_atomic(self, path: str, data: bytes) -> None:
        """Replace the whole entry with ``data``."""
        with self._lock:
            self._entries[path] = bytes(data)

    async def append_line(self, path: str, line: str) -> None:
        """Append ``line`` and a newline, creating the entry if absent."""
        if "\n" in line:
            raise ValueError("a line holds no newline")
        with self._lock:
            self._entries[path] = self._entries.get(path, b"") + line.encode() + b"\n"

    async def create_exclusive(self, path: str, data: bytes) -> bool:
        """Create the entry; return False and change nothing when it exists."""
        with self._lock:
            if path in self._entries:
                return False
            self._entries[path] = bytes(data)
            return True

    async def list_entries(self, directory: str) -> tuple[str, ...]:
        """Return the sorted names directly inside ``directory``."""
        prefix = directory.strip("/") + "/" if directory.strip("/") else ""
        with self._lock:
            names = {
                path[len(prefix) :].split("/", 1)[0]
                for path in self._entries
                if path.startswith(prefix)
            }
        return tuple(sorted(names))

    async def remove(self, path: str) -> bool:
        """Remove the entry; return False when it did not exist."""
        with self._lock:
            return self._entries.pop(path, None) is not None


class InMemoryTreeLock:
    """A non-blocking lock table; every grant gets a token no other grant shares."""

    def __init__(self) -> None:
        self._holders: dict[str, str] = {}
        self._counter = itertools.count(1)
        self._lock = threading.Lock()

    def acquire(self, key: str) -> str | None:
        """Take the lock on ``key`` without waiting; None when it is held."""
        with self._lock:
            if key in self._holders:
                return None
            token = f"grant-{next(self._counter)}"
            self._holders[key] = token
            return token

    def inspect(self, key: str) -> str | None:
        """Return the token now holding ``key``, or None when it is free."""
        with self._lock:
            return self._holders.get(key)

    def release(self, key: str, token: str) -> bool:
        """Release ``key`` if ``token`` is the current grant."""
        with self._lock:
            if self._holders.get(key) != token:
                return False
            del self._holders[key]
            return True


class InMemoryContainmentUnit:
    """Units as sets of simulated process ids."""

    def __init__(self) -> None:
        self._members: dict[str, set[int]] = {}
        self._undrainable: set[str] = set()
        self._pids = itertools.count(1000)
        self._lock = threading.Lock()

    def run_contained(self, unit: str, argv: Sequence[str]) -> int:
        """Record ``argv`` as started inside the new unit; return its process id."""
        if not argv:
            raise ValueError("argv names a command")
        with self._lock:
            if self._members.get(unit):
                raise InvalidProtocolStateError(f"unit {unit} already has members")
            pid = next(self._pids)
            self._members[unit] = {pid}
            return pid

    def members(self, unit: str) -> tuple[int, ...]:
        """Return the sorted process ids in ``unit``."""
        with self._lock:
            return tuple(sorted(self._members.get(unit, ())))

    def stop(self, unit: str, timeout_s: float) -> bool:
        """Kill every member; False only for a unit made undrainable."""
        del timeout_s
        with self._lock:
            if unit in self._undrainable:
                return False
            self._members.pop(unit, None)
            return True

    def spawn_detached(self, unit: str) -> int:
        """Add a member that is not the unit's main command; return its process id."""
        with self._lock:
            pid = next(self._pids)
            self._members.setdefault(unit, set()).add(pid)
            return pid

    def make_undrainable(self, unit: str) -> None:
        """Make ``stop`` fail for ``unit``, as a unit with a member that survives a kill."""
        with self._lock:
            self._undrainable.add(unit)


HostHandler = Callable[[ModelHostCallRequest], ModelHostCallAnswer | None]


class InMemoryHostCall:
    """A host whose behaviour per operation is arranged by the test.

    An operation with no arrangement, and an arranged silence, answer ``unknown``.
    A handler may return None to stay silent.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, HostHandler] = {}
        self.requests: list[ModelHostCallRequest] = []

    def arrange(self, operation: str, handler: HostHandler) -> None:
        """Answer ``operation`` with whatever ``handler`` returns."""
        self._handlers[operation] = handler

    def arrange_ok(self, operation: str, fields: dict[str, str]) -> None:
        """Answer ``operation`` ok with ``fields``."""
        self.arrange(
            operation,
            lambda r: ModelHostCallAnswer(
                request_id=r.request_id, outcome="ok", fields=dict(fields)
            ),
        )

    def arrange_refused(self, operation: str, cause: str) -> None:
        """Answer ``operation`` refused with ``cause``."""
        self.arrange(
            operation,
            lambda r: ModelHostCallAnswer(
                request_id=r.request_id, outcome="refused", cause=cause
            ),
        )

    def arrange_silence(self, operation: str) -> None:
        """Never answer ``operation``."""
        self.arrange(operation, lambda _request: None)

    def call(
        self,
        request: ModelHostCallRequest,
        timeout_s: float,
    ) -> ModelHostCallAnswer:
        """Return the arranged answer, or ``unknown`` when the host is silent."""
        del timeout_s
        self.requests.append(request)
        handler = self._handlers.get(request.operation)
        answer = handler(request) if handler is not None else None
        if answer is None:
            return ModelHostCallAnswer(request_id=request.request_id, outcome="unknown")
        return answer


class InMemoryGitRemote:
    """Remote branch heads in a dict; a push is accepted only under a holding lease."""

    def __init__(self) -> None:
        self._heads: dict[str, str] = {}
        self._lock = threading.Lock()

    def seed(self, branch: str, sha: str) -> None:
        """Point ``branch`` at ``sha`` directly, as a push by someone else."""
        with self._lock:
            self._heads[branch] = sha

    async def remote_head(self, branch: str) -> str | None:
        """Return the sha ``branch`` points at, or None when it does not exist."""
        with self._lock:
            return self._heads.get(branch)

    async def push_with_lease(
        self, sha: str, branch: str, expected_head: str | None
    ) -> ModelPushResult:
        """Push ``sha`` only if the branch is at ``expected_head``."""
        with self._lock:
            current = self._heads.get(branch)
            if current == sha:
                return ModelPushResult(pushed=True, remote_head=sha)
            if current != expected_head:
                return ModelPushResult(
                    pushed=False, cause="lease-stale", remote_head=current
                )
            self._heads[branch] = sha
            return ModelPushResult(pushed=True, remote_head=sha)


class InMemoryLaneHostTransport:
    """A scripted lane host: records every call in order, and the test scripts the engine.

    A start answers ``started`` unless the test scripts another state with
    ``script_start``. An engine ends only when the test calls ``script_exit`` or a
    stop reaches it; an engine marked ``script_stubborn`` survives every stop.
    """

    synchronous_execution = True

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self._start_state: str = "started"
        self._refusing: str | None = None
        self._running: set[str] = set()
        self._exit_codes: dict[str, int] = {}
        self._stubborn: set[str] = set()
        self._logs: dict[str, list[str]] = {}
        self._failing_steps: dict[str, str] = {}
        self.staged: dict[tuple[str, str], str] = {}

    def script_step_failure(self, method: str, error: str | None) -> None:
        """Make the provisioning call ``method`` fail with ``error``; None makes it succeed again."""
        if error is None:
            self._failing_steps.pop(method, None)
        else:
            self._failing_steps[method] = error

    def _step(self, method: str, request: ModelLaneHostStepRequest) -> str | None:
        self.calls.append((method, request.run_id))
        return self._failing_steps.get(method)

    def _plain_step(
        self, method: str, request: ModelLaneHostStepRequest
    ) -> ModelLaneHostStepResult:
        error = self._step(method, request)
        if error is not None:
            return ModelLaneHostStepResult(ok=False, error=error)
        return ModelLaneHostStepResult(ok=True, cells=(("step", method),))

    def _stage(
        self, method: str, request: ModelLaneStageInputRequest
    ) -> ModelLaneStagedInput:
        self.calls.append((method, request.run_id))
        error = self._failing_steps.get(method)
        if error is not None:
            return ModelLaneStagedInput(staged=False, error=error)
        self.staged[(request.run_id, request.name)] = request.content
        return ModelLaneStagedInput(
            staged=True, path=f"/runs/{request.run_id}.ctx/{request.name}"
        )

    def resolve_registry_root(
        self, request: ModelLaneHostStepRequest
    ) -> ModelLaneRegistryRootResult:
        """Return ``/omni``, or the scripted failure."""
        error = self._step("resolve_registry_root", request)
        if error is not None:
            return ModelLaneRegistryRootResult(error=error)
        return ModelLaneRegistryRootResult(registry_root="/omni")

    def prepare_run_dirs(
        self, request: ModelLaneHostStepRequest
    ) -> ModelLaneRunDirsResult:
        """Return the run and context directories, or the scripted failure."""
        error = self._step("prepare_run_dirs", request)
        if error is not None:
            return ModelLaneRunDirsResult(error=error)
        return ModelLaneRunDirsResult(
            run_dir=f"/runs/{request.run_id}", context_dir=f"/runs/{request.run_id}.ctx"
        )

    def stage_ledger_snapshot(
        self, request: ModelLaneStageInputRequest
    ) -> ModelLaneStagedInput:
        """Keep the snapshot in ``staged``, or the scripted failure."""
        return self._stage("stage_ledger_snapshot", request)

    def stage_file(self, request: ModelLaneStageInputRequest) -> ModelLaneStagedInput:
        """Keep the file in ``staged``, or the scripted failure."""
        return self._stage("stage_file", request)

    def ship_plugin_trees(
        self, request: ModelLaneShipPluginTreesRequest
    ) -> ModelLaneShipPluginTreesResult:
        """Return a directory per tree, or the scripted failure."""
        self.calls.append(("ship_plugin_trees", request.run_id))
        error = self._failing_steps.get("ship_plugin_trees")
        if error is not None:
            return ModelLaneShipPluginTreesResult(shipped=False, error=error)
        return ModelLaneShipPluginTreesResult(
            shipped=True,
            plugin_dirs=tuple(
                (tree.name, f"/plugins/{tree.source_digest}/{tree.name}")
                for tree in request.trees
            ),
        )

    def mirror_ledger(
        self, request: ModelLaneHostStepRequest
    ) -> ModelLaneHostStepResult:
        """A scripted step."""
        return self._plain_step("mirror_ledger", request)

    def write_runtime_config(
        self, request: ModelLaneHostStepRequest
    ) -> ModelLaneHostStepResult:
        """A scripted step."""
        return self._plain_step("write_runtime_config", request)

    def drain_guard_spool(
        self, request: ModelLaneHostStepRequest
    ) -> ModelLaneHostStepResult:
        """A scripted step."""
        return self._plain_step("drain_guard_spool", request)

    def relay_reports(
        self, request: ModelLaneHostStepRequest
    ) -> ModelLaneHostStepResult:
        """A scripted step."""
        return self._plain_step("relay_reports", request)

    def read_ledger_outbox(
        self, request: ModelLaneHostStepRequest
    ) -> ModelLaneLedgerOutboxRows:
        """No queued rows, or the scripted failure."""
        error = self._step("read_ledger_outbox", request)
        return ModelLaneLedgerOutboxRows(error=error)

    def read_lane_changes(
        self, request: ModelLaneHostStepRequest
    ) -> ModelLaneChangeList:
        """No changes, or the scripted failure."""
        error = self._step("read_lane_changes", request)
        return ModelLaneChangeList(error=error)

    def closeout_worktrees(
        self, request: ModelLaneHostStepRequest
    ) -> ModelLaneCloseoutCells:
        """One removed-worktree cell, or the scripted failure."""
        error = self._step("closeout_worktrees", request)
        if error is not None:
            return ModelLaneCloseoutCells(error=error)
        return ModelLaneCloseoutCells(
            cells=(f"worktree=removed:omni_worktrees/{request.lane}",)
        )

    def hold_run_dir_guard(
        self, request: ModelLaneHostStepRequest
    ) -> ModelLaneHostStepResult:
        """A scripted step."""
        return self._plain_step("hold_run_dir_guard", request)

    def retain_run_artifacts(
        self, request: ModelLaneHostStepRequest
    ) -> ModelLaneHostStepResult:
        """A scripted step."""
        return self._plain_step("retain_run_artifacts", request)

    def stop_lane_guard(
        self, request: ModelLaneHostStepRequest
    ) -> ModelLaneHostStepResult:
        """A scripted step."""
        return self._plain_step("stop_lane_guard", request)

    def script_start(self, state: str) -> None:
        """Make the next starts settle as ``started``, ``failed`` or ``unresolved``."""
        self._start_state = state

    def script_prepare_refusal(self, error: str | None) -> None:
        """Make prepare_worktree fail with ``error``; None makes it succeed again."""
        self._refusing = error

    def script_exit(self, run_id: str, exit_code: int) -> None:
        """End the run's engine with ``exit_code``."""
        self._running.discard(run_id)
        self._exit_codes[run_id] = exit_code

    def script_stubborn(self, run_id: str) -> None:
        """Make the run's engine survive every stop."""
        self._stubborn.add(run_id)

    def script_log(self, run_id: str, lines: Sequence[str]) -> None:
        """Set the run's engine log."""
        self._logs[run_id] = list(lines)

    def prepare_worktree(
        self, request: ModelLanePrepareWorktreeRequest
    ) -> ModelLanePrepareWorktreeResult:
        """Return a workdir under the first candidate registry_root, or the scripted refusal."""
        self.calls.append(("prepare_worktree", request.run_id))
        if self._refusing is not None:
            return ModelLanePrepareWorktreeResult(prepared=False, error=self._refusing)
        registry_root = (
            request.registry_root_candidates[0]
            if request.registry_root_candidates
            else "/omni"
        )
        return ModelLanePrepareWorktreeResult(
            prepared=True,
            registry_root=registry_root,
            workdir=f"{registry_root}/omni_worktrees/{request.lane}/{request.repo}",
        )

    def start_engine_detached(
        self, request: ModelLaneStartEngineRequest
    ) -> ModelLaneStartEngineResult:
        """Settle the start as scripted; a started engine is running."""
        self.calls.append(("start_engine_detached", request.run_id))
        if self._start_state == "started":
            self._running.add(request.run_id)
            return ModelLaneStartEngineResult(
                state="started", session_id=f"session-{request.run_id}"
            )
        if self._start_state == "failed":
            return ModelLaneStartEngineResult(
                state="failed", error="engine exited at start"
            )
        return ModelLaneStartEngineResult(state="unresolved")

    def read_engine_exit(
        self, request: ModelLaneReadEngineExitRequest
    ) -> ModelLaneReadEngineExitResult:
        """Return the exit code once the engine has ended, else running."""
        self.calls.append(("read_engine_exit", request.run_id))
        if request.run_id in self._exit_codes:
            return ModelLaneReadEngineExitResult(
                running=False, exit_code=self._exit_codes[request.run_id]
            )
        return ModelLaneReadEngineExitResult(running=True)

    def stop_engine(
        self, request: ModelLaneStopEngineRequest
    ) -> ModelLaneStopEngineResult:
        """End the engine unless it is stubborn; confirmed says whether it ended."""
        self.calls.append(("stop_engine", request.run_id))
        if request.run_id in self._stubborn:
            return ModelLaneStopEngineResult(confirmed=False, detail="engine survived")
        if request.run_id in self._exit_codes:
            return ModelLaneStopEngineResult(
                confirmed=True, exit_code=self._exit_codes[request.run_id]
            )
        self.script_exit(request.run_id, -15)
        return ModelLaneStopEngineResult(confirmed=True, exit_code=-15)

    def read_log_tail(
        self, request: ModelLaneReadLogTailRequest
    ) -> ModelLaneReadLogTailResult:
        """Return the log lines from the offset and the offset to read next."""
        self.calls.append(("read_log_tail", request.run_id))
        log = self._logs.get(request.run_id, [])
        return ModelLaneReadLogTailResult(
            lines=tuple(log[request.offset :]),
            next_offset=max(request.offset, len(log)),
        )


class InMemoryLaneHostPool:
    """A pool that returns the snapshot the test scripted, and records each request."""

    synchronous_execution = True

    def __init__(self, snapshot: ModelLaneHostPoolSnapshot | None = None) -> None:
        self.snapshot = snapshot or ModelLaneHostPoolSnapshot()
        self.requests: list[ModelLaneHostPoolRequest] = []

    def read_pool(self, request: ModelLaneHostPoolRequest) -> ModelLaneHostPoolSnapshot:
        """Return the scripted snapshot."""
        self.requests.append(request)
        return self.snapshot


class InMemoryLaneProcessRunner:
    """A scripted process runner: records each spec in order, and the test scripts the outcome."""

    synchronous_execution = True

    def __init__(self) -> None:
        self.calls: list[tuple[str, ModelLaneStartSpec]] = []
        self._start: ModelLaneProcessStartResult = ModelLaneProcessStartResult(
            state="started", pid=4242
        )
        self._run: ModelLaneProcessRunResult = ModelLaneProcessRunResult(
            state="exited", exit_code=0
        )

    def script_start(self, result: ModelLaneProcessStartResult) -> None:
        """Set what the next detached starts answer."""
        self._start = result

    def script_run(self, result: ModelLaneProcessRunResult) -> None:
        """Set what the next bounded runs answer."""
        self._run = result

    def start_detached(self, spec: ModelLaneStartSpec) -> ModelLaneProcessStartResult:
        """Record the spec and return the scripted start."""
        self.calls.append(("start_detached", spec))
        return self._start

    def run_bounded(
        self, spec: ModelLaneStartSpec, timeout_seconds: float
    ) -> ModelLaneProcessRunResult:
        """Record the spec and return the scripted run."""
        self.calls.append(("run_bounded", spec))
        return self._run


class InMemoryWorkLedgerStore:
    """A ledger held as raw lines; a row belongs to the lane its ``lane=`` cell names."""

    def __init__(self) -> None:
        self._rows: list[str] = []
        self._queued: dict[tuple[str, str], list[str]] = {}

    def append(self, row: str) -> None:
        """Add a raw ledger line after the existing ones."""
        self._rows.append(row)

    def queue(self, lane: str, run_id: str, row: str) -> None:
        """Record a row the lane queued on its host for relay."""
        self._queued.setdefault((lane, run_id), []).append(row)

    @staticmethod
    def _lane_of(row: str) -> str | None:
        for cell in row.replace("|", " ").split():
            if cell.startswith("lane="):
                return cell[len("lane=") :]
        return None

    def rows_for_lane(self, lane: str) -> tuple[str, ...]:
        """Return the lane's rows, oldest first."""
        return tuple(row for row in self._rows if self._lane_of(row) == lane)

    def queued_rows(self, lane: str, run_id: str) -> tuple[str, ...]:
        """Return the rows the lane queued in ``run_id``."""
        return tuple(self._queued.get((lane, run_id), ()))
