# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""In-memory adapters for the five lander protocols (OMN-22185).

They live with the conformance suites, not in the package: the omnibase_spi purity
gate allows no concrete class in ``src``. Each is the ``local``-profile adapter of
its protocol and passes the same checks as any real adapter.
"""

import itertools
import threading
from collections.abc import Callable, Sequence

from omnibase_spi.contracts.services import ModelHostCallAnswer, ModelHostCallRequest
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
