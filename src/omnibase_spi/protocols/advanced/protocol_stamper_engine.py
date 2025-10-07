# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.295679'
# description: Stamped by ToolPython
# entrypoint: python://protocol_stamper_engine
# hash: 5eb7ebbdf4d39d3c3f66ee78b1def44c00a1ebbf6b8c7c6fbab81d09f12c3216
# last_modified_at: '2025-05-29T14:14:00.345867+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_stamper_engine.py
# namespace: python://omnibase.protocol.protocol_stamper_engine
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: e2f209d1-3e49-47e0-9fd5-6732dd51d4e6
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types import ProtocolOnexResult


@runtime_checkable
class ProtocolStamperEngine(Protocol):
    """
    Protocol for batch metadata stamping operations across files and directories.

    Defines the contract for stamping engines that process individual files and
    entire directory trees with ONEX metadata blocks. Supports template selection,
    pattern-based filtering, and comprehensive stamping workflows for large-scale
    metadata management operations.

    Example:
        ```python
        from omnibase_spi.protocols.advanced import ProtocolStamperEngine
        from omnibase_spi.protocols.types import ProtocolOnexResult

        async def stamp_project(
            engine: ProtocolStamperEngine,
            project_dir: str
        ) -> ProtocolOnexResult:
            # Stamp all Python files in project recursively
            result = await engine.process_directory(
                directory=project_dir,
                template="STANDARD",
                recursive=True,
                include_patterns=["*.py"],
                exclude_patterns=["__pycache__/*", "*.pyc"],
                author="OmniNode Team",
                overwrite=False
            )

            print(f"Stamped {result.data.get('files_processed')} files")
            print(f"Skipped: {result.data.get('files_skipped')}")
            print(f"Errors: {result.data.get('files_failed')}")

            return result
        ```

    Key Features:
        - Batch file stamping with template support
        - Directory tree processing with recursion
        - Pattern-based file filtering (include/exclude)
        - Dry-run mode for validation before stamping
        - Repair mode for fixing corrupt metadata
        - Force overwrite for existing stamps
        - Comprehensive operation reporting

    See Also:
        - ProtocolStamper: Single file stamping operations
        - ProtocolOutputFormatter: Metadata formatting and rendering
        - ProtocolFixtureLoader: Fixture-based metadata templates
    """

    async def stamp_file(
        self,
        path: str,
        template: str | None = None,
        overwrite: bool | None = None,
        repair: bool | None = None,
        force_overwrite: bool | None = None,
        author: str | None = None,
        **kwargs: object,
    ) -> ProtocolOnexResult: ...

    async def process_directory(
        self,
        directory: str,
        template: str | None = None,
        recursive: bool | None = None,
        dry_run: bool | None = None,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        ignore_file: str | None = None,
        author: str | None = None,
        overwrite: bool | None = None,
        repair: bool | None = None,
        force_overwrite: bool | None = None,
    ) -> ProtocolOnexResult: ...
