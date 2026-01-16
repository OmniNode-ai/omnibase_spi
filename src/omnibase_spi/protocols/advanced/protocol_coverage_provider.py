"""Protocol for test coverage providers with multi-format support."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolCoverageProvider(Protocol):
    """
    Protocol for test coverage providers with multi-format support.

    Defines a standard interface for extracting test coverage percentage from various
    coverage report formats (XML, JSON, HTML, etc.). Enables consistent coverage
    analysis across different testing frameworks and report generators while providing
    extensibility for custom coverage calculation logic.

    Example:
        ```python
        from omnibase_spi.protocols.advanced import ProtocolCoverageProvider

        async def analyze_coverage(
            provider: ProtocolCoverageProvider,
            coverage_file: str
        ) -> float:
            # Extract coverage percentage from report
            coverage = await provider.get_coverage_percentage(coverage_file)

            # Evaluate against quality thresholds
            if coverage >= 80.0:
                print(f"Coverage {coverage}% meets quality target")
            else:
                print(f"Coverage {coverage}% below 80% target")

            return coverage
        ```

    Key Features:
        - Multi-format coverage report parsing (XML, JSON, HTML)
        - Framework-agnostic coverage extraction
        - Scenario-driven and custom coverage calculation support
        - Percentage normalization to 0-100 scale
        - Extensible for custom coverage metrics

    See Also:
        - ProtocolFixtureLoader: Test fixture loading and management
        - ProtocolDirectKnowledgePipeline: Coverage tracking in knowledge systems
        - ProtocolAnalyticsProvider: Coverage metrics and analytics
    """

    async def get_coverage_percentage(self, source: str) -> float:
        """
        Extract the test coverage percentage from the given source file or directory.

        Args:
            source: Path to the coverage report or data source

        Returns:
            Coverage percentage as a float (0-100)

        Raises:
            FileNotFoundError: If source file does not exist
            ValueError: If coverage cannot be determined from source
            Exception: If source format is invalid or parsing fails
        """
        ...
