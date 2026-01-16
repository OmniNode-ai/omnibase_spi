"""Protocol for loading ONEX version information.

This module defines the interface for loading version information from .onexversion files.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ProtocolVersionInfo


@runtime_checkable
class ProtocolVersionLoader(Protocol):
    """
    Protocol for loading ONEX version information from .onexversion files.
    """

    async def get_onex_versions(self) -> ProtocolVersionInfo:
        """
        Load ONEX version information from .onexversion files.

        Retrieves version information for the ONEX platform including
        core version, protocol versions, and compatibility information.

        Returns:
            ProtocolVersionInfo: Version information object containing
                platform and protocol version details.

        Raises:
            VersionFileNotFoundError: When .onexversion file cannot be found.
            VersionParseError: When version file format is invalid.
        """
        ...
