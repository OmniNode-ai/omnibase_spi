"""Protocol for pattern extraction operations.

This module defines the protocol for extracting patterns from session data.
Implementations analyze sessions to identify file access patterns, error patterns,
architecture patterns, and tool usage patterns.

Supported Pattern Kinds:
- FILE_ACCESS: Co-access, entry points, modification clusters
- ERROR: Error-prone files, error sequences
- ARCHITECTURE: Module boundaries, layers
- TOOL_USAGE: Sequences, preferences, success rates

Example:
    >>> class MyExtractor:
    ...     async def extract_patterns(
    ...         self, input_data: ModelPatternExtractionInput
    ...     ) -> ModelPatternExtractionOutput:
    ...         # Implementation here
    ...         ...
    >>>
    >>> # Check protocol compliance
    >>> assert isinstance(MyExtractor(), ProtocolPatternExtractor)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.intelligence import (
        ModelPatternExtractionInput,
        ModelPatternExtractionOutput,
    )

__all__ = ["ProtocolPatternExtractor"]


@runtime_checkable
class ProtocolPatternExtractor(Protocol):
    """Protocol for pattern extraction operations.

    Defines the interface for extracting patterns from session data.
    Implementations should analyze input sessions and return extraction results
    with confidence scores and pattern categorization.

    The protocol supports 4 pattern kinds via EnumPatternKind:
    - FILE_ACCESS: File co-access, entry points, modification clusters
    - ERROR: Error-prone files, error sequences
    - ARCHITECTURE: Module boundaries, layer patterns
    - TOOL_USAGE: Tool sequences, preferences, success rates

    Example:
        >>> async def example():
        ...     extractor: ProtocolPatternExtractor = get_extractor()
        ...     result = await extractor.extract_patterns(input_data)
        ...     print(f"Found {result.total_patterns_found} patterns")
    """

    async def extract_patterns(
        self,
        input_data: ModelPatternExtractionInput,
    ) -> ModelPatternExtractionOutput:
        """Extract patterns from session data.

        Analyzes sessions in input_data and identifies patterns across
        file access, errors, architecture, and tool usage.

        Args:
            input_data: Input containing session data to analyze.
                Contains fields: session_ids, kinds (optional filter),
                min_occurrences, min_confidence, time_window_start/end,
                raw_events (optional), correlation_id, schema_version.

        Returns:
            Extraction result containing:
                - success: Whether extraction succeeded
                - patterns_by_kind: Dict mapping EnumPatternKind to pattern lists
                - total_patterns_found: Total count of extracted patterns
                - processing_time_ms: Extraction duration
                - sessions_analyzed: Number of sessions processed
                - warnings/errors: Structured issues (not exceptions)
                - deterministic: Whether output is reproducible
                - correlation_id, source_snapshot_id: Traceability

        Raises:
            May raise implementation-specific exceptions for invalid input
            or extraction failures beyond the structured error surface.
        """
        ...
