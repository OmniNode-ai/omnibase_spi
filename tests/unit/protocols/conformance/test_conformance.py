# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""OMN-22185: every adapter passes each protocol's conformance suite; every suite refuses a broken adapter.

Adapters under test: the in-memory adapter beside each protocol, and a reference
adapter over the real filesystem, git or process table where one is practical in a
test. The production adapters belong to the omnimarket nodes that bind them
(task L2 and L3 of the lane lander plan) and plug into the same checks unchanged.
Each suite's positive control is a broken adapter that the checks must refuse.
"""

import inspect
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from omnibase_spi.contracts.services import ModelHostCallAnswer, ModelHostCallRequest
from omnibase_spi.contracts.source_control import ModelPushResult
from tests.unit.protocols.conformance import (
    suite_containment_unit,
    suite_durable_store,
    suite_git_remote,
    suite_host_call,
    suite_tree_lock,
)
from tests.unit.protocols.conformance.adapters_in_memory import (
    InMemoryContainmentUnit,
    InMemoryDurableStore,
    InMemoryGitRemote,
    InMemoryHostCall,
    InMemoryTreeLock,
)
from tests.unit.protocols.conformance.adapters_reference import (
    EnvMarkerContainmentUnit,
    FilesystemDurableStore,
    FilesystemTreeLock,
    LocalGitHarness,
)

# ---------------------------------------------------------------- harnesses


class _InMemoryGitHarness:
    def __init__(self, remote: Any = None) -> None:
        self.remote = remote or InMemoryGitRemote()
        self._n = 0

    def new_commit(self, parent: str | None) -> str:
        self._n += 1
        return f"{self._n:040x}"

    def seed(self, branch: str, sha: str) -> None:
        self.remote.seed(branch, sha)


class _InMemoryContainmentHarness:
    long_running_argv = ("sleep", "60")

    def __init__(self, unit: Any = None) -> None:
        self.unit = unit or InMemoryContainmentUnit()

    def add_detached_member(self, unit: str) -> int:
        return self.unit.spawn_detached(unit)


class _ReferenceContainmentHarness:
    long_running_argv = ("sleep", "60")

    def __init__(self) -> None:
        self.unit = EnvMarkerContainmentUnit()

    def add_detached_member(self, unit: str) -> int:
        return self.unit.spawn_detached(unit, self.long_running_argv)


class _InMemoryHostHarness:
    def __init__(self, host: Any = None) -> None:
        self.host = host or InMemoryHostCall()

    def arrange_ok(self, operation: str, fields: dict[str, str]) -> None:
        self.host.arrange_ok(operation, fields)

    def arrange_refused(self, operation: str, cause: str) -> None:
        self.host.arrange_refused(operation, cause)

    def arrange_silence(self, operation: str) -> None:
        self.host.arrange_silence(operation)


# ---------------------------------------------------------- broken adapters


class _BrokenDurableStore(InMemoryDurableStore):
    """create_exclusive overwrites instead of refusing."""

    async def create_exclusive(self, path: str, data: bytes) -> bool:
        await self.write_atomic(path, data)
        return True


class _BrokenTreeLock(InMemoryTreeLock):
    """release ignores the token."""

    def release(self, key: str, token: str) -> bool:
        return super().release(key, self.inspect(key) or token)


class _BrokenGitRemote(InMemoryGitRemote):
    """push ignores the lease."""

    async def push_with_lease(
        self, sha: str, branch: str, expected_head: str | None
    ) -> ModelPushResult:
        return await super().push_with_lease(
            sha, branch, await self.remote_head(branch)
        )


class _BrokenContainmentUnit(InMemoryContainmentUnit):
    """stop reports empty while members remain."""

    def stop(self, unit: str, timeout_s: float) -> bool:
        return True


class _BrokenHostCall(InMemoryHostCall):
    """A silent host is reported as ok."""

    def call(
        self, request: ModelHostCallRequest, timeout_s: float
    ) -> ModelHostCallAnswer:
        answer = super().call(request, timeout_s)
        if answer.outcome == "unknown":
            return ModelHostCallAnswer(request_id=request.request_id, outcome="ok")
        return answer


# ------------------------------------------------------------------- suites


def _ids(checks: tuple[Callable[..., None], ...]) -> list[str]:
    return [c.__name__ for c in checks]


@pytest.mark.unit
@pytest.mark.parametrize(
    "check", suite_durable_store.CHECKS, ids=_ids(suite_durable_store.CHECKS)
)
@pytest.mark.parametrize("kind", ["in_memory", "filesystem"])
async def test_durable_store_conformance(
    kind: str, check: Callable[..., Any], tmp_path: Path
) -> None:
    store = (
        InMemoryDurableStore()
        if kind == "in_memory"
        else FilesystemDurableStore(tmp_path)
    )
    result = check(store)
    if inspect.isawaitable(result):
        await result


@pytest.mark.unit
@pytest.mark.parametrize(
    "check", suite_tree_lock.CHECKS, ids=_ids(suite_tree_lock.CHECKS)
)
@pytest.mark.parametrize("kind", ["in_memory", "filesystem"])
def test_tree_lock_conformance(
    kind: str, check: Callable[..., None], tmp_path: Path
) -> None:
    lock = InMemoryTreeLock() if kind == "in_memory" else FilesystemTreeLock(tmp_path)
    check(lock)


@pytest.mark.unit
@pytest.mark.parametrize(
    "check", suite_git_remote.CHECKS, ids=_ids(suite_git_remote.CHECKS)
)
@pytest.mark.parametrize("kind", ["in_memory", "local_git"])
async def test_git_remote_conformance(
    kind: str, check: Callable[..., Any], tmp_path: Path
) -> None:
    harness: Any = (
        _InMemoryGitHarness() if kind == "in_memory" else LocalGitHarness(tmp_path)
    )
    result = check(harness)
    if inspect.isawaitable(result):
        await result


@pytest.mark.unit
@pytest.mark.parametrize(
    "check", suite_containment_unit.CHECKS, ids=_ids(suite_containment_unit.CHECKS)
)
@pytest.mark.parametrize("kind", ["in_memory", "process_table"])
def test_containment_unit_conformance(kind: str, check: Callable[..., None]) -> None:
    harness: Any = (
        _InMemoryContainmentHarness()
        if kind == "in_memory"
        else _ReferenceContainmentHarness()
    )
    check(harness)


@pytest.mark.unit
@pytest.mark.parametrize(
    "check", suite_host_call.CHECKS, ids=_ids(suite_host_call.CHECKS)
)
def test_host_call_conformance(check: Callable[..., None]) -> None:
    check(_InMemoryHostHarness())


# ----------------------------------------------------------- positive controls


@pytest.mark.unit
async def test_control_durable_store_suite_refuses_an_overwriting_create() -> None:
    with pytest.raises(AssertionError):
        await suite_durable_store.check_create_exclusive_keeps_the_first(
            _BrokenDurableStore()
        )
    with pytest.raises(AssertionError):
        await suite_durable_store.check_create_exclusive_races_leave_one_winner(
            _BrokenDurableStore()
        )


@pytest.mark.unit
def test_control_tree_lock_suite_refuses_a_token_blind_release() -> None:
    with pytest.raises(AssertionError):
        suite_tree_lock.check_a_stale_token_leaves_the_new_holder(_BrokenTreeLock())


@pytest.mark.unit
async def test_control_git_remote_suite_refuses_a_push_that_ignores_the_lease() -> None:
    with pytest.raises(AssertionError):
        await suite_git_remote.check_a_stale_lease_is_refused_and_the_remote_unchanged(
            _InMemoryGitHarness(_BrokenGitRemote())
        )


@pytest.mark.unit
def test_control_containment_suite_refuses_a_stop_that_leaves_members() -> None:
    with pytest.raises(AssertionError):
        suite_containment_unit.check_stop_kills_every_member_and_confirms_empty(
            _InMemoryContainmentHarness(_BrokenContainmentUnit())
        )


@pytest.mark.unit
def test_control_host_call_suite_refuses_silence_reported_as_ok() -> None:
    with pytest.raises(AssertionError):
        suite_host_call.check_no_answer_in_time_is_unknown_and_does_not_raise(
            _InMemoryHostHarness(_BrokenHostCall())
        )


@pytest.mark.unit
def test_control_the_reference_git_adapter_really_runs_git(tmp_path: Path) -> None:
    harness = LocalGitHarness(tmp_path)
    commit = harness.new_commit(None)
    out = subprocess.run(
        [shutil.which("git") or "git", "cat-file", "-t", commit],
        cwd=tmp_path / "work",
        capture_output=True,
        text=True,
        check=True,
    )
    assert out.stdout.strip() == "commit"


@pytest.mark.unit
def test_in_memory_containment_unit_can_be_made_undrainable() -> None:
    unit = InMemoryContainmentUnit()
    unit.run_contained("stuck", ["sleep", "60"])
    unit.make_undrainable("stuck")
    assert unit.stop("stuck", 0.01) is False
    assert len(unit.members("stuck")) == 1
    unit.run_contained("fine", ["sleep", "60"])
    assert unit.stop("fine", 0.01) is True
