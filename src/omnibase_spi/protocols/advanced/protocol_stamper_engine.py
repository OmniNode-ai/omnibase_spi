"""Protocol for batch metadata stamping operations.

This module defines the interface for stamping engines that process files and
directories with ONEX metadata blocks at scale.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types import ProtocolResult


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
        from omnibase_spi.protocols.types import ProtocolResult

        async def stamp_project(
            engine: ProtocolStamperEngine,
            project_dir: str
        ) -> ProtocolResult:
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
    ) -> ProtocolResult:
        """Stamp a single file with ONEX metadata.

        Generates and injects ONEX metadata block into the specified file
        using the selected template and options.

        Args:
            path: Path to the file to stamp.
            template: Template type for metadata generation (e.g., "MINIMAL",
                "STANDARD", "FULL"). Defaults to engine configuration.
            overwrite: Whether to overwrite existing metadata blocks.
                Defaults to False.
            repair: Whether to attempt repair of corrupt metadata blocks.
                Defaults to False.
            force_overwrite: Whether to force overwrite even if metadata
                appears valid. Defaults to False.
            author: Author attribution for the metadata block.
            **kwargs: Additional template-specific options.

        Returns:
            ProtocolResult with success status and operation details
            including the generated hash and metadata summary.

        Raises:
            FileNotFoundError: If the specified path does not exist.
            PermissionError: If the file cannot be read or written.
            ValueError: If the file format is not supported or template
                is invalid.
        """
        ...

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
    ) -> ProtocolResult:
        """Process and stamp all matching files in a directory.

        Recursively or non-recursively processes files in the specified
        directory, applying ONEX metadata stamps based on pattern matching
        and configuration options.

        Args:
            directory: Path to the directory to process.
            template: Template type for metadata generation (e.g., "MINIMAL",
                "STANDARD", "FULL"). Defaults to engine configuration.
            recursive: Whether to process subdirectories recursively.
                Defaults to True.
            dry_run: Whether to simulate stamping without modifying files.
                Defaults to False.
            include_patterns: Glob patterns for files to include
                (e.g., ["*.py", "*.yaml"]).
            exclude_patterns: Glob patterns for files to exclude
                (e.g., ["__pycache__/*", "*.pyc"]).
            ignore_file: Path to ignore file (e.g., ".onexignore") containing
                additional exclusion patterns.
            author: Author attribution for all stamped metadata blocks.
            overwrite: Whether to overwrite existing metadata blocks.
                Defaults to False.
            repair: Whether to attempt repair of corrupt metadata blocks.
                Defaults to False.
            force_overwrite: Whether to force overwrite even if metadata
                appears valid. Defaults to False.

        Returns:
            ProtocolResult with success status and operation summary
            including files_processed, files_skipped, files_failed counts
            and detailed per-file results.

        Raises:
            FileNotFoundError: If the specified directory does not exist.
            PermissionError: If the directory cannot be read or files
                cannot be written.
            ValueError: If the template is invalid or patterns are malformed.
        """
        ...
