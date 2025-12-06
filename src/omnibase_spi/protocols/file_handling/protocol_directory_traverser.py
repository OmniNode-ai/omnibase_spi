# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.117773'
# description: Stamped by ToolPython
# entrypoint: python://protocol_directory_traverser
# hash: 774dc0903eac6c14d4cd9a2aefb2642124debaed178d33f5e784de8bc43484b5
# last_modified_at: '2025-05-29T14:14:00.213326+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_directory_traverser.py
# namespace: python://omnibase.protocol.protocol_directory_traverser
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: c5431a51-699a-4674-abd7-431b5ed0046a
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Protocol for directory traversal operations.
Defines a standardized interface for discovering and filtering files in directories.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue

T = TypeVar("T")  # Generic type variable for processor result


@runtime_checkable
class ProtocolDirectoryProcessingResult(Protocol):
    """
    Protocol for directory processing results.

    Defines the contract for directory processing operation results
    with comprehensive statistics and file tracking.
    """

    processed_files: int
    skipped_files: int
    failed_files: int
    total_files: int
    processing_time_ms: float
    file_results: list[dict[str, "ContextValue"]]
    errors: list[str]


@runtime_checkable
class ProtocolDirectoryTraverser(Protocol):
    """
    Protocol for directory traversal operations in ONEX ecosystem.

    Defines the standardized interface for discovering and filtering files
    in directories with comprehensive pattern matching and processing capabilities.

    Key Features:
        - Flexible file discovery with glob patterns
        - Ignore file support (.gitignore, .onexignore patterns)
        - Recursive directory traversal with depth control
        - File processing with custom processor functions
        - Dry-run mode for safe validation
        - Comprehensive statistics and error tracking

    Supported Operations:
        - File discovery with inclusion/exclusion patterns
        - Ignore pattern loading and matching
        - Directory processing with custom handlers
        - Size-based filtering and validation
        - Performance monitoring and metrics

    Usage Example:
        ```python
        traverser: ProtocolDirectoryTraverser = SomeDirectoryTraverser()

        # Discover files with pattern filtering
        files = traverser.find_files(
            directory=str('/project'),
            include_patterns=['*.py', '*.yaml'],
            exclude_patterns=['**/__pycache__/**', '**/.git/**'],
            recursive=True
        )

        # Process directory with custom processor
        def process_file(file_path: str) -> dict:
            return {"path": str(file_path), "size": file_path.stat().st_size}

        result = traverser.process_directory(
            directory=str('/project/src'),
            processor=process_file,
            include_patterns=['*.py'],
            dry_run=False
        )

        print(f"Processed {result.processed_files} files")
        ```

    Integration Patterns:
        - Works with ONEX file processing pipelines
        - Integrates with validation and stamping workflows
        - Supports multiple discovery strategies
        - Provides comprehensive processing statistics
    """

    def find_files(
        self,
        directory: str,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        recursive: bool | None = None,
        ignore_file: str | None = None,
    ) -> set[str]:
        """
        Find all files matching the given patterns in the directory.

        Args:
            directory: Directory to search
            include_patterns: List of glob patterns to include (e.g., ['**/*.yaml'])
            exclude_patterns: List of glob patterns to exclude (e.g., ['**/.git/**'])
            recursive: Whether to recursively traverse subdirectories
            ignore_file: str to ignore file (e.g., .onexignore)

        Returns:
            Set of str objects for matching files
        """
        ...

    async def load_ignore_patterns(
        self, ignore_file: str | None = None
    ) -> list[str]: ...
    def should_ignore(self, path: str, ignore_patterns: list[str]) -> bool:
        """
        Check if a file should be ignored based on patterns.

        Args:
            path: str to check
            ignore_patterns: List of ignore patterns

        Returns:
            True if the file should be ignored, False otherwise
        """
        ...

    async def process_directory(
        self,
        directory: str,
        processor: Callable[[str], T],
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        recursive: bool | None = None,
        ignore_file: str | None = None,
        dry_run: bool | None = None,
        max_file_size: int | None = None,
    ) -> "ProtocolDirectoryProcessingResult":
        """
        Process all eligible files in a directory using the provided processor function.

        Args:
            directory: Directory to process
            processor: Callable[..., Any]that processes each file and returns a result
            include_patterns: List of glob patterns to include
            exclude_patterns: List of glob patterns to exclude
            recursive: Whether to recursively traverse subdirectories
            ignore_file: str to ignore file (e.g., .onexignore)
            dry_run: Whether to perform a dry run (don't modify files)
            max_file_size: Maximum file size in bytes to process

        Returns:
            ModelDirectoryProcessingResult with aggregate results and file stats
        """
        ...
