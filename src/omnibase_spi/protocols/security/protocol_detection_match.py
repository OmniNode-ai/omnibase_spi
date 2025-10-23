"""
Protocol for Detection Match

Defines the minimal interface that models need from ModelDetectionMatch
to break circular import dependencies.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolDetectionMatch(Protocol):
    """
    Protocol defining the minimal interface for detection matches.

    This protocol allows models to type-hint detection match parameters without
    importing the concrete ModelDetectionMatch class, breaking circular dependencies.
    """

    @property
    def start_position(self) -> int:
        """Start character position of the match."""
        ...

    @property
    def end_position(self) -> int:
        """End character position of the match."""
        ...

    @property
    def matched_text(self) -> str:
        """The actual text that was detected."""
        ...

    @property
    def confidence_score(self) -> float:
        """Confidence score for this detection (0-1)."""
        ...
