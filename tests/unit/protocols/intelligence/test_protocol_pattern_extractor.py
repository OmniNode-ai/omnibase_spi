"""Tests for ProtocolPatternExtractor protocol compliance.

Validates that ProtocolPatternExtractor:
- Is properly runtime checkable
- Defines required methods with correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

from __future__ import annotations

import inspect
from typing import Any, Protocol

import pytest

from omnibase_spi.protocols.intelligence import ProtocolPatternExtractor

# =============================================================================
# Mock Models (since we can't import from omnibase_core in tests)
# =============================================================================


class MockPatternExtractionInput:
    """Mock that simulates ModelPatternExtractionInput from omnibase_core.

    Provides the minimal interface needed for testing ProtocolPatternExtractor.
    """

    def __init__(
        self,
        session_ids: list[str] | None = None,
        kinds: list[str] | None = None,
        min_occurrences: int = 2,
        min_confidence: float = 0.5,
        correlation_id: str | None = None,
        schema_version: str = "1.0.0",
    ) -> None:
        """Initialize the mock input."""
        self.session_ids = session_ids or []
        self.kinds = kinds
        self.min_occurrences = min_occurrences
        self.min_confidence = min_confidence
        self.correlation_id = correlation_id
        self.schema_version = schema_version


class MockPatternExtractionOutput:
    """Mock that simulates ModelPatternExtractionOutput from omnibase_core.

    Provides the minimal interface needed for testing ProtocolPatternExtractor.
    """

    def __init__(
        self,
        success: bool = True,
        patterns_by_kind: dict[str, list[dict[str, Any]]] | None = None,
        total_patterns_found: int = 0,
        processing_time_ms: float = 0.0,
        sessions_analyzed: int = 0,
        warnings: list[dict[str, Any]] | None = None,
        errors: list[dict[str, Any]] | None = None,
        deterministic: bool = True,
        correlation_id: str | None = None,
    ) -> None:
        """Initialize the mock output."""
        self.success = success
        self.patterns_by_kind = patterns_by_kind or {}
        self.total_patterns_found = total_patterns_found
        self.processing_time_ms = processing_time_ms
        self.sessions_analyzed = sessions_analyzed
        self.warnings = warnings or []
        self.errors = errors or []
        self.deterministic = deterministic
        self.correlation_id = correlation_id


# =============================================================================
# Mock Implementations
# =============================================================================


class MockPatternExtractor:
    """A class that fully implements the ProtocolPatternExtractor protocol.

    This mock implementation provides a simple extractor for testing.
    It demonstrates how a compliant implementation should behave.
    """

    async def extract_patterns(
        self,
        input_data: Any,  # Would be ModelPatternExtractionInput
    ) -> Any:  # Would be ModelPatternExtractionOutput
        """Extract patterns from session data.

        Args:
            input_data: Input containing session data to analyze.

        Returns:
            Extraction result with patterns categorized by kind.
        """
        return MockPatternExtractionOutput(
            success=True,
            patterns_by_kind={
                "FILE_ACCESS": [{"pattern": "co-access", "confidence": 0.85}],
            },
            total_patterns_found=1,
            processing_time_ms=42.5,
            sessions_analyzed=len(getattr(input_data, "session_ids", [])),
        )


class NonCompliantExtractor:
    """A class that does not implement the ProtocolPatternExtractor protocol."""

    pass


class PartialExtractor:
    """A class that has a method with the wrong name."""

    async def extract(self, input_data: Any) -> Any:
        """Wrong method name - should be extract_patterns."""
        return None


class SyncExtractor:
    """A class that has a sync method instead of async."""

    def extract_patterns(self, input_data: Any) -> Any:
        """Sync method - should be async."""
        return MockPatternExtractionOutput()


class WrongSignatureExtractor:
    """A class with extract_patterns but wrong signature (no parameters)."""

    async def extract_patterns(self) -> Any:
        """Missing input_data parameter."""
        return MockPatternExtractionOutput()


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestProtocolPatternExtractorProtocol:
    """Test suite for ProtocolPatternExtractor protocol definition."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolPatternExtractor should be runtime_checkable.

        Runtime checkable protocols have either _is_runtime_protocol
        or __runtime_protocol__ attribute set to True.
        """
        # Check for either the old or new attribute name for runtime protocols
        assert hasattr(ProtocolPatternExtractor, "_is_runtime_protocol") or hasattr(
            ProtocolPatternExtractor, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolPatternExtractor should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolPatternExtractor.__mro__
        )

    def test_protocol_has_extract_patterns_method(self) -> None:
        """ProtocolPatternExtractor should define extract_patterns method."""
        assert "extract_patterns" in dir(ProtocolPatternExtractor)

    def test_protocol_method_is_async(self) -> None:
        """The extract_patterns method should be a coroutine function."""
        # Get the method from the protocol
        method = getattr(ProtocolPatternExtractor, "extract_patterns", None)
        assert method is not None

        # Check if it's defined as async (coroutine function)
        # For protocols, we check the method signature
        assert inspect.iscoroutinefunction(method)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolPatternExtractor should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolPatternExtractor()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolPatternExtractorCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance_check(self) -> None:
        """A class implementing the protocol should pass isinstance check."""
        extractor = MockPatternExtractor()
        assert isinstance(extractor, ProtocolPatternExtractor)

    def test_non_compliant_class_fails_isinstance_check(self) -> None:
        """A class not implementing the protocol should fail isinstance check."""
        not_an_extractor = NonCompliantExtractor()
        assert not isinstance(not_an_extractor, ProtocolPatternExtractor)

    def test_partial_implementation_fails_isinstance_check(self) -> None:
        """A class with wrong method name should fail isinstance check."""
        partial = PartialExtractor()
        assert not isinstance(partial, ProtocolPatternExtractor)

    def test_sync_method_still_passes_isinstance_check(self) -> None:
        """A class with sync method passes isinstance (runtime check is structural).

        Note: Python's runtime protocol checking only verifies attribute presence,
        not whether it's async. This is a limitation of runtime_checkable.
        Static type checkers would catch this issue.
        """
        sync_extractor = SyncExtractor()
        # Runtime check only verifies method exists, not that it's async
        assert isinstance(sync_extractor, ProtocolPatternExtractor)

    def test_wrong_signature_still_passes_isinstance_check(self) -> None:
        """A class with wrong signature passes isinstance (runtime check is structural).

        Note: Python's runtime protocol checking only verifies attribute presence,
        not the full method signature. Static type checkers would catch this.
        """
        wrong_sig = WrongSignatureExtractor()
        # Runtime check only verifies method exists
        assert isinstance(wrong_sig, ProtocolPatternExtractor)


@pytest.mark.unit
class TestMockPatternExtractorImplementation:
    """Test that MockPatternExtractor has all required members."""

    def test_mock_has_extract_patterns_method(self) -> None:
        """Mock should have extract_patterns method."""
        extractor = MockPatternExtractor()
        assert hasattr(extractor, "extract_patterns")
        assert callable(extractor.extract_patterns)

    def test_mock_extract_patterns_is_async(self) -> None:
        """Mock extract_patterns should be async."""
        extractor = MockPatternExtractor()
        assert inspect.iscoroutinefunction(extractor.extract_patterns)

    @pytest.mark.asyncio
    async def test_mock_extract_patterns_returns_output(self) -> None:
        """Mock should return extraction output."""
        extractor = MockPatternExtractor()
        input_data = MockPatternExtractionInput(
            session_ids=["session-1", "session-2"],
            kinds=["FILE_ACCESS"],
            min_occurrences=2,
            min_confidence=0.5,
        )

        result = await extractor.extract_patterns(input_data)

        assert result is not None
        assert result.success is True
        assert result.total_patterns_found == 1
        assert "FILE_ACCESS" in result.patterns_by_kind
        assert result.sessions_analyzed == 2

    @pytest.mark.asyncio
    async def test_mock_extract_patterns_handles_empty_input(self) -> None:
        """Mock should handle empty session input."""
        extractor = MockPatternExtractor()
        input_data = MockPatternExtractionInput(session_ids=[])

        result = await extractor.extract_patterns(input_data)

        assert result is not None
        assert result.success is True
        assert result.sessions_analyzed == 0


@pytest.mark.unit
class TestProtocolPatternExtractorImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol_pattern_extractor module."""
        from omnibase_spi.protocols.intelligence.protocol_pattern_extractor import (
            ProtocolPatternExtractor as DirectProtocolPatternExtractor,
        )

        extractor = MockPatternExtractor()
        assert isinstance(extractor, DirectProtocolPatternExtractor)

    def test_protocol_exports_from_intelligence_module(self) -> None:
        """Protocol should be importable from intelligence module."""
        from omnibase_spi.protocols.intelligence import (
            ProtocolPatternExtractor as IntelligenceProtocolPatternExtractor,
        )

        extractor = MockPatternExtractor()
        assert isinstance(extractor, IntelligenceProtocolPatternExtractor)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.intelligence import (
            ProtocolPatternExtractor as IntelligenceProtocolPatternExtractor,
        )
        from omnibase_spi.protocols.intelligence.protocol_pattern_extractor import (
            ProtocolPatternExtractor as DirectProtocolPatternExtractor,
        )

        assert DirectProtocolPatternExtractor is IntelligenceProtocolPatternExtractor

    def test_protocol_exports_from_main_module(self) -> None:
        """Protocol should be importable from main protocols module."""
        from omnibase_spi.protocols import (
            ProtocolPatternExtractor as MainProtocolPatternExtractor,
        )

        extractor = MockPatternExtractor()
        assert isinstance(extractor, MainProtocolPatternExtractor)


@pytest.mark.unit
class TestProtocolPatternExtractorDocumentation:
    """Test that ProtocolPatternExtractor has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolPatternExtractor should have a docstring."""
        assert ProtocolPatternExtractor.__doc__ is not None
        assert len(ProtocolPatternExtractor.__doc__.strip()) > 0

    def test_docstring_mentions_pattern_extraction(self) -> None:
        """Docstring should mention pattern extraction purpose."""
        doc = ProtocolPatternExtractor.__doc__ or ""
        assert "pattern" in doc.lower()

    def test_docstring_mentions_pattern_kinds(self) -> None:
        """Docstring should mention supported pattern kinds."""
        doc = ProtocolPatternExtractor.__doc__ or ""
        # Should mention at least one of the 4 pattern kinds
        kinds = [
            "FILE_ACCESS",
            "ERROR",
            "ARCHITECTURE",
            "TOOL_USAGE",
        ]
        assert any(kind in doc for kind in kinds)

    def test_extract_patterns_method_has_docstring(self) -> None:
        """The extract_patterns method should have a docstring."""
        method = getattr(ProtocolPatternExtractor, "extract_patterns", None)
        assert method is not None
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0


@pytest.mark.unit
class TestPatternKinds:
    """Test that the protocol documents all 4 pattern kinds."""

    def test_protocol_documents_file_access_kind(self) -> None:
        """Protocol docstring should document FILE_ACCESS pattern kind."""
        doc = ProtocolPatternExtractor.__doc__ or ""
        assert "FILE_ACCESS" in doc, "Missing pattern kind: FILE_ACCESS"

    def test_protocol_documents_error_kind(self) -> None:
        """Protocol docstring should document ERROR pattern kind."""
        doc = ProtocolPatternExtractor.__doc__ or ""
        assert "ERROR" in doc, "Missing pattern kind: ERROR"

    def test_protocol_documents_architecture_kind(self) -> None:
        """Protocol docstring should document ARCHITECTURE pattern kind."""
        doc = ProtocolPatternExtractor.__doc__ or ""
        assert "ARCHITECTURE" in doc, "Missing pattern kind: ARCHITECTURE"

    def test_protocol_documents_tool_usage_kind(self) -> None:
        """Protocol docstring should document TOOL_USAGE pattern kind."""
        doc = ProtocolPatternExtractor.__doc__ or ""
        assert "TOOL_USAGE" in doc, "Missing pattern kind: TOOL_USAGE"

    def test_protocol_documents_all_pattern_kinds(self) -> None:
        """Protocol docstring should document all 4 pattern kinds."""
        doc = ProtocolPatternExtractor.__doc__ or ""
        pattern_kinds = [
            "FILE_ACCESS",
            "ERROR",
            "ARCHITECTURE",
            "TOOL_USAGE",
        ]
        for kind in pattern_kinds:
            assert kind in doc, f"Missing pattern kind: {kind}"
