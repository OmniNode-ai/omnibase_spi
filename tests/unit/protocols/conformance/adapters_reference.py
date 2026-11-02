# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Reference adapters over the real filesystem, git and process table.

They plug into the same conformance checks as the in-memory adapters, which
proves each suite holds a real implementation to the protocol and not only the
in-memory one. The production adapters (a flock lock, systemd scopes, the Redpanda
topic pair for host calls) belong to the omnimarket nodes that bind them.
"""

import contextlib
import os
import shutil
import signal
import subprocess
import time
import uuid
from collections.abc import Sequence
from pathlib import Path

from omnibase_spi.contracts.source_control import ModelPushResult
from omnibase_spi.exceptions import InvalidProtocolStateError

_GIT = shutil.which("git") or "git"


class FilesystemDurableStore:
    """ProtocolDurableStore over a directory."""

    def __init__(self, root: Path) -> None:
        self._root = root

    def _p(self, path: str) -> Path:
        return self._root / path

    async def read(self, path: str) -> bytes | None:
        try:
            return self._p(path).read_bytes()
        except FileNotFoundError:
            return None

    async def write_atomic(self, path: str, data: bytes) -> None:
        target = self._p(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
        tmp.write_bytes(data)
        tmp.replace(target)

    async def append_line(self, path: str, line: str) -> None:
        if "\n" in line:
            raise ValueError("a line holds no newline")
        target = self._p(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(target, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            os.write(fd, line.encode() + b"\n")
        finally:
            os.close(fd)

    async def create_exclusive(self, path: str, data: bytes) -> bool:
        target = self._p(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return False
        try:
            os.write(fd, data)
        finally:
            os.close(fd)
        return True

    async def list_entries(self, directory: str) -> tuple[str, ...]:
        target = self._p(directory)
        if not target.is_dir():
            return ()
        return tuple(sorted(entry.name for entry in target.iterdir()))

    async def remove(self, path: str) -> bool:
        try:
            self._p(path).unlink()
        except FileNotFoundError:
            return False
        return True


class FilesystemTreeLock:
    """ProtocolTreeLock over exclusive-create lock files holding the grant token."""

    def __init__(self, root: Path) -> None:
        self._root = root
        root.mkdir(parents=True, exist_ok=True)

    def _p(self, key: str) -> Path:
        return self._root / f"{key}.lock"

    def acquire(self, key: str) -> str | None:
        token = uuid.uuid4().hex
        try:
            fd = os.open(self._p(key), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return None
        try:
            os.write(fd, token.encode())
        finally:
            os.close(fd)
        return token

    def inspect(self, key: str) -> str | None:
        try:
            text = self._p(key).read_text()
        except FileNotFoundError:
            return None
        return text or None

    def release(self, key: str, token: str) -> bool:
        if self.inspect(key) != token:
            return False
        self._p(key).unlink(missing_ok=True)
        return True


class LocalGitRemote:
    """ProtocolGitRemote over a bare repository, driven through the git command line."""

    def __init__(self, bare: Path) -> None:
        self._bare = bare

    def _git(
        self, *args: str, cwd: Path | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [_GIT, *args],
            cwd=cwd or self._bare,
            capture_output=True,
            text=True,
            check=False,
        )

    def _remote_head(self, branch: str) -> str | None:
        out = self._git("rev-parse", "--verify", "--quiet", f"refs/heads/{branch}")
        return out.stdout.strip() or None

    async def remote_head(self, branch: str) -> str | None:
        return self._remote_head(branch)

    async def push_with_lease(
        self, sha: str, branch: str, expected_head: str | None
    ) -> ModelPushResult:
        expected = expected_head if expected_head is not None else ""
        out = self._git(
            "push",
            f"--force-with-lease=refs/heads/{branch}:{expected}",
            str(self._bare),
            f"{sha}:refs/heads/{branch}",
            cwd=self._work,
        )
        head = self._remote_head(branch)
        if out.returncode == 0:
            return ModelPushResult(pushed=True, remote_head=head)
        return ModelPushResult(pushed=False, cause="lease-stale", remote_head=head)

    _work: Path


class LocalGitHarness:
    """Harness: a bare remote plus a working clone that makes commits."""

    def __init__(self, root: Path) -> None:
        bare = root / "remote.git"
        work = root / "work"
        bare.mkdir()
        work.mkdir()
        for args, cwd in (
            (["init", "--bare", "--initial-branch=main", str(bare)], root),
            (["init", "--initial-branch=main", str(work)], root),
        ):
            subprocess.run([_GIT, *args], cwd=cwd, check=True, capture_output=True)
        self._work = work
        self.remote = LocalGitRemote(bare)
        self.remote._work = work
        self._bare = bare
        self._n = 0

    def new_commit(self, parent: str | None) -> str:
        self._n += 1
        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@example.invalid",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@example.invalid",
        }
        tree = subprocess.run(
            [_GIT, "hash-object", "-t", "tree", "-w", "--stdin"],
            cwd=self._work,
            input="",
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        args = [_GIT, "commit-tree", tree, "-m", f"c{self._n}"]
        if parent is not None:
            args += ["-p", parent]
        return subprocess.run(
            args, cwd=self._work, env=env, capture_output=True, text=True, check=True
        ).stdout.strip()

    def seed(self, branch: str, sha: str) -> None:
        subprocess.run(
            [_GIT, "push", str(self._bare), f"{sha}:refs/heads/{branch}"],
            cwd=self._work,
            check=True,
            capture_output=True,
        )


class EnvMarkerContainmentUnit:
    """ProtocolContainmentUnit that marks every process of a unit in its environment.

    Membership is read from /proc, so a descendant that detaches from the session
    or the process group is still a member.
    """

    _MARK = "ONEX_TEST_UNIT"

    def __init__(self) -> None:
        self._procs: dict[str, subprocess.Popen[bytes]] = {}

    def run_contained(self, unit: str, argv: Sequence[str]) -> int:
        if self.members(unit):
            raise InvalidProtocolStateError(f"unit {unit} already has members")
        proc = subprocess.Popen(
            list(argv),
            env={**os.environ, self._MARK: unit},
            start_new_session=True,
        )
        self._procs[unit] = proc
        return proc.pid

    def spawn_detached(self, unit: str, argv: Sequence[str]) -> int:
        proc = subprocess.Popen(
            list(argv), env={**os.environ, self._MARK: unit}, start_new_session=True
        )
        return proc.pid

    def members(self, unit: str) -> tuple[int, ...]:
        found: list[int] = []
        needle = f"{self._MARK}={unit}".encode()
        for entry in Path("/proc").iterdir():
            if not entry.name.isdigit():
                continue
            try:
                environ = (entry / "environ").read_bytes().split(b"\0")
                stat = (entry / "stat").read_text()
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue
            if needle in environ and stat.split(") ")[-1][0] != "Z":
                found.append(int(entry.name))
        return tuple(sorted(found))

    def stop(self, unit: str, timeout_s: float) -> bool:
        deadline = time.monotonic() + timeout_s
        while True:
            pids = self.members(unit)
            for pid in pids:
                with contextlib.suppress(ProcessLookupError):
                    os.kill(pid, signal.SIGKILL)
            proc = self._procs.get(unit)
            if proc is not None:
                proc.poll()
            if not self.members(unit):
                return True
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.02)
