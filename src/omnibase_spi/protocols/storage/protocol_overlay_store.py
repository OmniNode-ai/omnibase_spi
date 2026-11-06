# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for the store of loaded deployment overlays.

An overlay is the source of a deployment's configuration. A loader node puts one
overlay on the bus by its id and a projection holds it. Every reader reads it through
this protocol, whichever backend an overlay selects, so a reader never names a
database or a broker. A backend that cannot answer raises: an unreachable store and a
store that holds no such overlay are different facts, and the second is the ``None``
of :meth:`read_current`.
"""

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolOverlayStore(Protocol):
    """Write and read one version of one overlay as a JSON record."""

    async def write_version(self, record: Mapping[str, JsonType]) -> bool:
        """Make ``record`` the current version of the overlay it names.

        Returns:
            True when the store changed; False when it already held this load or a
            newer one.
        """
        ...

    async def read_current(self, overlay_id: str) -> Mapping[str, JsonType] | None:
        """The overlay's current version as a JSON record, or None when the store holds none."""
        ...


__all__ = ["ProtocolOverlayStore"]
