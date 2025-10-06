"""
Protocol for Version Management and Compatibility.

Defines interfaces for protocol versioning, compatibility checking,
and migration support across ONEX service evolution.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ProtocolCompatibilityCheck,
        ProtocolDateTime,
        ProtocolSemVer,
        ProtocolVersionInfo,
    )


@runtime_checkable
class ProtocolVersionManager(Protocol):
    """
    Protocol for version management and compatibility checking.

    Provides version metadata management, compatibility verification,
    and migration guidance for evolving protocol interfaces.

    Key Features:
        - Semantic version management for protocols
        - Backward and forward compatibility checking
        - Breaking change detection and migration guidance
        - Deprecation lifecycle management
        - Version negotiation for service communication
        - Migration path documentation and automation

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        class VersionManagerImpl:
            async def check_compatibility(self, required, current):
                if current.major != required.major:
                    return CompatibilityCheck(
                        is_compatible=False,
                        breaking_changes=["Major version mismatch"],
                        migration_required=True
                    )
                return CompatibilityCheck(is_compatible=True)

        # Usage in application code
        version_manager: "ProtocolVersionManager" = VersionManagerImpl()

        compatibility = version_manager.check_compatibility(
            required_version=SemVer(2, 1, 0),
            current_version=SemVer(2, 0, 5)
        )

        if not compatibility.is_compatible:
            raise VersionError(compatibility.breaking_changes)
        ```
    """

    async def get_protocol_version_info(
        self, protocol_name: str
    ) -> "ProtocolVersionInfo": ...

    async def register_protocol_version(
        self,
        protocol_name: str,
        version: "ProtocolSemVer",
        compatibility_version: "ProtocolSemVer",
        migration_guide_url: str | None = None,
    ) -> bool: ...

    async def check_compatibility(
        self,
        protocol_name: str,
        required_version: "ProtocolSemVer",
        current_version: "ProtocolSemVer",
    ) -> "ProtocolCompatibilityCheck": ...

    async def get_breaking_changes(
        self,
        protocol_name: str,
        from_version: "ProtocolSemVer",
        to_version: "ProtocolSemVer",
    ) -> list[str]: ...

    def schedule_retirement(
        self,
        protocol_name: str,
        version: "ProtocolSemVer",
        retirement_date: "ProtocolDateTime",
        replacement_version: "ProtocolSemVer | None" = None,
    ) -> bool: ...

    async def get_retired_versions(
        self, protocol_name: str
    ) -> list["ProtocolVersionInfo"]: ...

    def is_version_retired(
        self, protocol_name: str, version: "ProtocolSemVer"
    ) -> bool: ...

    async def get_recommended_version(
        self, protocol_name: str, current_version: "ProtocolSemVer"
    ) -> "ProtocolSemVer": ...

    async def generate_migration_plan(
        self,
        protocol_name: str,
        from_version: "ProtocolSemVer",
        to_version: "ProtocolSemVer",
    ) -> dict[str, object]: ...

    async def validate_version_usage(
        self, protocol_name: str, version: "ProtocolSemVer"
    ) -> list[str]: ...

    async def get_version_statistics(
        self, time_window_days: int
    ) -> dict[str, object]: ...
