"""
Protocol interface for pre-commit checker tools in ONEX ecosystem.

This protocol defines the interface for pre-commit checker tools that validate
code quality, SPI purity, and compliance before commits. Provides type-safe
contracts for consistent checking behavior across different validation types.

Domain: Validation and Quality Assurance
Author: ONEX Framework Team
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolModelCheckResult(Protocol):
    """
    Protocol for pre-commit check results.

    Defines the contract for validation results from pre-commit checking operations.
    Provides comprehensive result reporting with violation tracking and summary statistics.

    Key Features:
        - Success/failure status indication
        - Detailed violation tracking
        - Summary statistics generation
        - File count tracking
        - Violation filtering capabilities

    Usage Example:
        ```python
        result: ProtocolModelCheckResult = checker.check_files([file1, file2])

        if result.has_violations():
            print(f"Found {result.get_violation_count()} violations")
            for violation in result.violations:
                print(f"{violation.file_path}:{violation.line_number} - {violation.message}")
        else:
            print("No violations found")
        ```
    """

    success: bool
    violations: list["ProtocolCheckViolation"]
    summary: dict[str, int]
    checked_files: int

    def has_violations(self) -> bool:
        """
            ...
        Check if any violations were found.

        Returns:
            True if violations exist, False otherwise
        """
        ...

    async def get_violation_count(self) -> int: ...
    async def get_summary_dict(self) -> dict[str, int]:
        """
        Get summary statistics as dictionary.

        Returns:
            Dictionary with summary statistics
        """
        ...


@runtime_checkable
class ProtocolCheckViolation(Protocol):
    """
    Protocol for check violation details.

    Defines the contract for individual violation records with detailed
    location and severity information for accurate reporting.

    Key Features:
        - File path and line number location
        - Rule identification and severity
        - Detailed error messages
        - Serialization for reporting
        - Integration with issue tracking

    Usage Example:
        ```python
        violation: ProtocolCheckViolation = some_violation

        # Convert to dictionary for reporting
        violation_data = violation.to_dict()
        report_violation(violation_data)

        # Access violation details
        if violation.severity == "error":
            handle_critical_violation(violation)
        ```
    """

    file_path: str
    line_number: int | None
    rule_id: str
    severity: str
    message: str

    def to_dict(self) -> dict[str, str | int | None]:
        """
        Convert violation to dictionary representation.

        Returns:
            Dictionary with violation details
        """
        ...


@runtime_checkable
class ProtocolPrecommitChecker(Protocol):
    """
    Base protocol for pre-commit checker tools in ONEX ecosystem.

    Defines the interface for pre-commit checker tools that validate code quality,
    SPI purity, and compliance before commits. Provides consistent checking behavior
    across different validation types with comprehensive result reporting.

    Key Features:
        - File and directory validation
        - Batch processing support
        - Detailed violation reporting
        - Integration with CI/CD pipelines
        - Configurable validation rules
        - Performance optimization

    Supported Validation Types:
        - SPI purity validation (namespace isolation, protocol compliance)
        - Code quality checks (style, formatting, best practices)
        - Security validation (vulnerability scanning)
        - Performance analysis (bottleneck detection)
        - Documentation validation (completeness, accuracy)

    Usage Example:
        ```python
        checker: ProtocolPrecommitChecker = SomePrecommitChecker()

        # Check multiple files
        files_to_check = [str('src/main.py'), str('tests/test_main.py')]
        result = checker.check_files(files_to_check)

        if result.has_violations():
            print(f"Found {result.get_violation_count()} violations")
            # Handle violations
            handle_violations(result.violations)
        else:
            print("All checks passed")

        # Check single file
        single_result = checker.check_single_file(str('config.yaml'))
        ```

    Integration Patterns:
        - Works with ONEX validation framework
        - Integrates with git pre-commit hooks
        - Supports CI/CD pipeline integration
        - Provides detailed violation reporting
        - Compatible with async processing patterns
    """

    async def check_files(self, file_paths: list[str]) -> "ProtocolModelCheckResult":
        """
        Check files for violations.

        Performs comprehensive validation of the specified files according to the
        checker's validation rules and quality standards.

        Args:
            file_paths: List of file paths to check
                ...
        Returns:
            ProtocolModelCheckResult with violations and summary
        """
        ...

    async def check_single_file(self, file_path: str) -> "ProtocolModelCheckResult":
        """
        Check a single file for violations.

        Performs focused validation on a single file with detailed reporting
        of any violations found.

        Args:
            file_path: str to file to check
                ...
        Returns:
            ProtocolModelCheckResult with violations found
        """
        ...
