# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Protocol for the remote side of a git repository.

The one write is a push of a sha to a branch that is accepted only while the
remote branch still points at the head the caller expected, so two pushes from
one base cannot both land.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.source_control import ModelPushResult


@runtime_checkable
class ProtocolGitRemote(Protocol):
    """Read a remote branch head and push to it under a lease."""

    async def remote_head(self, branch: str) -> str | None:
        """Return the sha ``branch`` points at on the remote, or None when it does not exist."""
        ...

    async def push_with_lease(
        self, sha: str, branch: str, expected_head: str | None
    ) -> "ModelPushResult":
        """Push ``sha`` to ``branch`` only if the remote branch is at ``expected_head``.

        ``expected_head`` None means the branch must not exist. A lease that no
        longer holds is refused with cause ``lease-stale`` and the remote is unchanged. A push of the sha the branch already points at is accepted
        as a no-op.
        """
        ...


__all__ = ["ProtocolGitRemote"]
