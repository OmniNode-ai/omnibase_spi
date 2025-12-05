"""
CLI Directory Fixture Case Protocol for ONEX CLI Interface

Defines the protocol interface for directory fixture case handling in CLI operations,
providing standardized structure for test fixture management.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolFileEntry(Protocol):
    """
    Protocol for individual file entry within a directory fixture.

    Represents a single file with its relative path and content for
    test fixture creation, enabling reproducible test directory
    structures in CLI testing workflows.

    Attributes:
        relative_path: Path relative to fixture base directory
        content: Full text content of the file

    Example:
        ```python
        fixture: ProtocolCLIDirFixtureCase = get_test_fixture()

        for file_entry in fixture.files:
            full_path = f"{base_path}/{file_entry.relative_path}"
            print(f"File: {full_path}")
            print(f"  Content length: {len(file_entry.content)} chars")
        ```

    See Also:
        - ProtocolSubdirEntry: Subdirectory with files
        - ProtocolCLIDirFixtureCase: Complete fixture definition
    """

    relative_path: str
    content: str


@runtime_checkable
class ProtocolSubdirEntry(Protocol):
    """
    Protocol for subdirectory entry within a directory fixture.

    Represents a subdirectory containing multiple files for nested
    fixture structure creation in CLI testing workflows, enabling
    complex directory hierarchies for integration testing.

    Attributes:
        subdir: Subdirectory name relative to parent
        files: List of file entries within this subdirectory

    Example:
        ```python
        fixture: ProtocolCLIDirFixtureCase = get_test_fixture()

        if fixture.subdirs:
            for subdir_entry in fixture.subdirs:
                print(f"Subdirectory: {subdir_entry.subdir}")
                for file_entry in subdir_entry.files:
                    print(f"  File: {file_entry.relative_path}")
        ```

    See Also:
        - ProtocolFileEntry: Individual file definition
        - ProtocolCLIDirFixtureCase: Complete fixture container
    """

    subdir: str
    files: list["ProtocolFileEntry"]


@runtime_checkable
class ProtocolCLIDirFixtureCase(Protocol):
    """
    Protocol for CLI directory fixture case management.

    Provides structured test fixture management for CLI testing including
    fixture creation, validation, and cleanup with support for complex
    directory hierarchies and file content.

    Attributes:
        id: Unique identifier for this fixture case
        files: List of root-level file entries
        subdirs: Optional list of subdirectory entries

    Example:
        ```python
        fixture: ProtocolCLIDirFixtureCase = load_fixture_case("test-case-001")

        # Create fixture at test location
        base_path = "/tmp/test-fixtures"
        success = await fixture.create_fixture(base_path)

        if success:
            # Run tests against fixture
            result = await run_cli_tests(base_path)

            # Validate fixture integrity
            is_valid = await fixture.validate_fixture(base_path)

            # Clean up after tests
            await fixture.cleanup_fixture(base_path)
        ```

    See Also:
        - ProtocolFileEntry: File content definitions
        - ProtocolSubdirEntry: Subdirectory structures
        - ProtocolCLI: CLI execution against fixtures
    """

    id: str
    files: list["ProtocolFileEntry"]
    subdirs: list["ProtocolSubdirEntry"] | None

    async def create_fixture(self, base_path: str) -> bool:
        """
        Create the directory fixture at the specified path.

        Args:
            base_path: Base path where fixture should be created

        Returns:
            True if fixture creation succeeded, False otherwise
        """
        ...

    async def validate_fixture(self, base_path: str) -> bool:
        """
        Validate that the directory fixture exists and is correct.

        Args:
            base_path: Base path to validate fixture against

        Returns:
            True if fixture is valid, False otherwise
        """
        ...

    async def cleanup_fixture(
        self, base_path: str, timeout_seconds: float = 30.0
    ) -> bool:
        """
        Clean up the directory fixture.

        Args:
            base_path: Base path where fixture should be cleaned up
            timeout_seconds: Maximum time to wait for cleanup to complete.
                Defaults to 30.0 seconds.

        Returns:
            True if cleanup succeeded, False otherwise

        Raises:
            TimeoutError: If cleanup does not complete within the specified timeout.
        """
        ...
