# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Checks every ProtocolGitRemote adapter must pass.

A real adapter is wrapped in a harness that can make a commit the remote can
receive and seed a remote branch; the in-memory adapter's harness does the same.
"""

from collections.abc import Awaitable, Callable
from typing import Protocol

from omnibase_spi.protocols.effects import ProtocolGitRemote


class GitRemoteHarness(Protocol):
    remote: ProtocolGitRemote

    def new_commit(self, parent: str | None) -> str:
        """Return the sha of a new commit that the remote can receive."""
        ...

    def seed(self, branch: str, sha: str) -> None:
        """Point the remote branch at ``sha`` directly."""
        ...


def check_is_protocol_instance(h: GitRemoteHarness) -> None:
    assert isinstance(h.remote, ProtocolGitRemote)


async def check_absent_branch_has_no_head(h: GitRemoteHarness) -> None:
    assert await h.remote.remote_head("nope") is None


async def check_push_creates_a_branch_that_must_not_exist(h: GitRemoteHarness) -> None:
    c1 = h.new_commit(None)
    result = await h.remote.push_with_lease(c1, "feat", None)
    assert result.pushed is True and result.cause is None
    assert await h.remote.remote_head("feat") == c1
    c2 = h.new_commit(c1)
    again = await h.remote.push_with_lease(c2, "feat", None)
    assert again.pushed is False and again.cause == "lease-stale"
    assert await h.remote.remote_head("feat") == c1


async def check_pushing_the_sha_already_there_is_a_noop_success(
    h: GitRemoteHarness,
) -> None:
    c1 = h.new_commit(None)
    h.seed("same", c1)
    result = await h.remote.push_with_lease(c1, "same", None)
    assert result.pushed is True
    assert await h.remote.remote_head("same") == c1


async def check_push_with_the_current_head_advances_it(h: GitRemoteHarness) -> None:
    c1 = h.new_commit(None)
    h.seed("adv", c1)
    c2 = h.new_commit(c1)
    result = await h.remote.push_with_lease(c2, "adv", c1)
    assert result.pushed is True
    assert await h.remote.remote_head("adv") == c2


async def check_a_stale_lease_is_refused_and_the_remote_unchanged(
    h: GitRemoteHarness,
) -> None:
    base = h.new_commit(None)
    h.seed("lease", base)
    left = h.new_commit(base)
    right = h.new_commit(base)
    first = await h.remote.push_with_lease(left, "lease", base)
    second = await h.remote.push_with_lease(right, "lease", base)
    assert first.pushed is True
    assert second.pushed is False and second.cause == "lease-stale"
    assert await h.remote.remote_head("lease") == left


CHECKS: tuple[Callable[[GitRemoteHarness], Awaitable[None] | None], ...] = (
    check_is_protocol_instance,
    check_absent_branch_has_no_head,
    check_push_creates_a_branch_that_must_not_exist,
    check_pushing_the_sha_already_there_is_a_noop_success,
    check_push_with_the_current_head_advances_it,
    check_a_stale_lease_is_refused_and_the_remote_unchanged,
)
