# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for the store of the lab host table.

The lab host table says which hosts may take work. An overlay is its source; a
loader node puts it on the bus and a projection holds it. Every reader reads it
through this protocol, whichever backend an overlay selects, so a reader never
names a database or a broker. A backend that cannot answer raises: an unreachable
store and a store that holds no table are different facts, and the second is the
``None`` of :meth:`read_current`.
"""

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolLabHostTableStore(Protocol):
    """Write and read one version of the lab host table as a JSON record."""

    async def write_version(self, record: Mapping[str, JsonType]) -> bool:
        """Make ``record`` the current version.

        Returns:
            True when the store changed; False when it already held this version
            or a newer one.
        """
        ...

    async def read_current(self) -> Mapping[str, JsonType] | None:
        """The current version as a JSON record, or None when the store holds none."""
        ...


__all__ = ["ProtocolLabHostTableStore"]
