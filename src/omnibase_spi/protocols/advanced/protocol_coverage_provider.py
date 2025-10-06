from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolCoverageProvider(Protocol):
    """
    Protocol for test coverage providers.
    Defines a standard interface for extracting test coverage percentage from a given source (e.g., coverage XML, JSON, scenario-driven, etc.).
    Implementations may parse different formats or use custom logic, but must return a float (0-100) representing coverage percentage.
    """

    async def get_coverage_percentage(self, source: str) -> float:
        """
            ...
        Extract the test coverage percentage from the given source file or directory.
        Args:
            source: str to the coverage report or data source.
        Returns:
            Coverage percentage as a float (0-100).
        Raises:
            Exception if coverage cannot be determined or source is invalid.
        """
        ...
