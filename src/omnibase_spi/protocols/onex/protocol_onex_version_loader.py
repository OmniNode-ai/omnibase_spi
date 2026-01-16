"""Protocol for loading ONEX version information.

This module defines the interface for loading version information from .onexversion files.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ProtocolVersionInfo


@runtime_checkable
class ProtocolToolToolOnexVersionLoader(Protocol):
    """
    Protocol for loading ONEX version information from .onexversion files.
    """

    async def get_onex_versions(self) -> ProtocolVersionInfo: ...
