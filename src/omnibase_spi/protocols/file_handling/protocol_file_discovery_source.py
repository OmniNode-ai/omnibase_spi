"""Protocol for file discovery sources (filesystem, .tree, hybrid, etc.).

Defines a standardized interface for discovering and validating files for stamping/validation.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolTreeSyncResult(Protocol):
    """
    Protocol for tree synchronization results.

    Defines the contract for tree synchronization validation results
    with drift detection and status reporting capabilities.
    """

    is_in_sync: bool
    drift_detected: bool
    missing_files: list[str]
    extra_files: list[str]
    modified_files: list[str]
    validation_timestamp: str


@runtime_checkable
class ProtocolFileDiscoverySource(Protocol):
    """
    Protocol for file discovery sources in ONEX ecosystem.

    Defines the standardized interface for discovering and validating files
    for stamping and validation operations. Supports multiple discovery
    strategies including filesystem scanning, .tree file parsing, and
    hybrid approaches.

    Key Features:
        - Flexible file discovery strategies
        - Pattern-based inclusion/exclusion filtering
        - Tree synchronization validation
        - Canonical file extraction from .tree files
        - Drift detection between filesystem and tree files

    Supported Discovery Strategies:
        - Filesystem: Direct directory scanning with glob patterns
        - Tree-based: Parsing .tree files for canonical file lists
        - Hybrid: Combining filesystem and tree-based approaches
        - Custom: Plugin-based discovery implementations

    Usage Example:
        ```python
        discovery: ProtocolFileDiscoverySource = SomeFileDiscoverySource()

        # Discover files with pattern filtering
        files = discovery.discover_files(
            directory=str('/project'),
            include_patterns=['*.py', '*.yaml'],
            exclude_patterns=['test_*'],
            ignore_file=str('.onexignore')
        )

        # Validate tree synchronization
        sync_result = discovery.validate_tree_sync(
            directory=str('/project'),
            tree_file=str('/project/.tree')
        )

        if sync_result.drift_detected:
            handle_tree_drift(sync_result)

        # Extract canonical files from tree
        canonical_files = discovery.get_canonical_files_from_tree(
            tree_file=str('/project/.tree')
        )
        ```

    Integration Patterns:
        - Works with ONEX file processing pipelines
        - Integrates with validation and stamping workflows
        - Supports multiple discovery strategy implementations
        - Provides comprehensive drift detection capabilities
    """

    def discover_files(
        self,
        directory: str,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        ignore_file: str | None = None,
    ) -> set[str]:
        """
        Discover eligible files for stamping/validation in the given directory.

        Performs comprehensive file discovery with pattern-based filtering
        and ignore file support. Provides flexible file selection for
        validation and stamping operations.

        Args:
            directory: Root directory to search for files
            include_patterns: Optional glob patterns to include (e.g., ['*.py', '*.yaml'])
            exclude_patterns: Optional glob patterns to exclude (e.g., ['test_*', '__pycache__'])
            ignore_file: Optional ignore file path (e.g., .onexignore, .gitignore)

        Returns:
            Set of str objects for eligible files matching criteria

        Example:
            ```python
            # Find all Python and YAML files, excluding test files
            files = discovery.discover_files(
                directory=str('/project/src'),
                include_patterns=['*.py', '*.yaml'],
                exclude_patterns=['test_*.py']
            )
            ```
        """
        ...

    async def validate_tree_sync(
        self, directory: str, tree_file: str
    ) -> ProtocolTreeSyncResult:
        """
        Validate that the .tree file and filesystem are in sync.

        Performs comprehensive synchronization validation between the
        filesystem state and the canonical .tree file representation.
        Detects drift, missing files, extra files, and modifications.

        Args:
            directory: Root directory to validate against tree file
            tree_file: str to .tree file containing canonical file list

        Returns:
            ProtocolTreeSyncResult with detailed drift information and validation status

        Example:
            ```python
            result = discovery.validate_tree_sync(
                directory=str('/project'),
                tree_file=str('/project/.tree')
            )

            if not result.is_in_sync:
                print(f"Drift detected: {len(result.missing_files)} missing, "
                      f"{len(result.extra_files)} extra files")
            ```
        """
        ...

    async def get_canonical_files_from_tree(
        self,
        tree_file: str,
    ) -> set[str]:
        """
        Get the set of canonical files listed in a .tree file.

        Extracts and returns the canonical file list from a .tree file,
        providing the expected file structure for validation purposes.

        Args:
            tree_file: str to .tree file containing canonical file list

        Returns:
            Set of str objects listed in the .tree file

        Example:
            ```python
            canonical_files = discovery.get_canonical_files_from_tree(
                tree_file=str('/project/.tree')
            )

            print(f"Found {len(canonical_files)} canonical files")
            for file_path in sorted(canonical_files):
                print(f"  {file_path}")
            ```
        """
        ...
