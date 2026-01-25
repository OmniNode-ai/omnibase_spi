# SPDX-License-Identifier: MIT
# Copyright (c) 2025 OmniNode Team
"""Tests for ProtocolIntentClassifier protocol compliance.

Validates that ProtocolIntentClassifier:
- Is properly runtime checkable
- Defines required methods with correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Protocol

import pytest

from omnibase_spi.protocols.intelligence import ProtocolIntentClassifier

if TYPE_CHECKING:
    from omnibase_core.models.intelligence import (
        ModelIntentClassificationInput,
        ModelIntentClassificationOutput,
    )


# =============================================================================
# Mock Models (since we can't import from omnibase_core in tests)
# =============================================================================


class MockIntentClassificationInput:
    """Mock that simulates ModelIntentClassificationInput from omnibase_core.

    Provides the minimal interface needed for testing ProtocolIntentClassifier.
    """

    def __init__(
        self,
        content: str = "",
        correlation_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the mock input."""
        self.content = content
        self.correlation_id = correlation_id
        self.context = context or {}


class MockIntentClassificationOutput:
    """Mock that simulates ModelIntentClassificationOutput from omnibase_core.

    Provides the minimal interface needed for testing ProtocolIntentClassifier.
    """

    def __init__(
        self,
        success: bool = True,
        intent_category: str = "code_generation",
        confidence: float = 0.95,
        secondary_intents: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the mock output."""
        self.success = success
        self.intent_category = intent_category
        self.confidence = confidence
        self.secondary_intents = secondary_intents or []
        self.metadata = metadata or {}


# =============================================================================
# Mock Implementations
# =============================================================================


class MockIntentClassifier:
    """A class that fully implements the ProtocolIntentClassifier protocol.

    This mock implementation provides a simple classifier for testing.
    It demonstrates how a compliant implementation should behave.
    """

    async def classify_intent(
        self,
        input_data: Any,  # Would be ModelIntentClassificationInput
    ) -> Any:  # Would be ModelIntentClassificationOutput
        """Classify user intent from input data.

        Args:
            input_data: Input containing content to classify.

        Returns:
            Classification result with intent category and confidence.
        """
        return MockIntentClassificationOutput(
            success=True,
            intent_category="code_generation",
            confidence=0.95,
        )


class NonCompliantClassifier:
    """A class that does not implement the ProtocolIntentClassifier protocol."""

    pass


class PartialClassifier:
    """A class that has a method with the wrong name."""

    async def classify(self, input_data: Any) -> Any:
        """Wrong method name - should be classify_intent."""
        return None


class SyncClassifier:
    """A class that has a sync method instead of async."""

    def classify_intent(self, input_data: Any) -> Any:
        """Sync method - should be async."""
        return MockIntentClassificationOutput()


class WrongSignatureClassifier:
    """A class with classify_intent but wrong signature (no parameters)."""

    async def classify_intent(self) -> Any:
        """Missing input_data parameter."""
        return MockIntentClassificationOutput()


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestProtocolIntentClassifierProtocol:
    """Test suite for ProtocolIntentClassifier protocol definition."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolIntentClassifier should be runtime_checkable.

        Runtime checkable protocols have either _is_runtime_protocol
        or __runtime_protocol__ attribute set to True.
        """
        # Check for either the old or new attribute name for runtime protocols
        assert hasattr(
            ProtocolIntentClassifier, "_is_runtime_protocol"
        ) or hasattr(ProtocolIntentClassifier, "__runtime_protocol__")

    def test_protocol_is_protocol(self) -> None:
        """ProtocolIntentClassifier should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolIntentClassifier.__mro__
        )

    def test_protocol_has_classify_intent_method(self) -> None:
        """ProtocolIntentClassifier should define classify_intent method."""
        assert "classify_intent" in dir(ProtocolIntentClassifier)

    def test_protocol_method_is_async(self) -> None:
        """The classify_intent method should be a coroutine function."""
        # Get the method from the protocol
        method = getattr(ProtocolIntentClassifier, "classify_intent", None)
        assert method is not None

        # Check if it's defined as async (coroutine function)
        # For protocols, we check the method signature
        assert inspect.iscoroutinefunction(method)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolIntentClassifier should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolIntentClassifier()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolIntentClassifierCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance_check(self) -> None:
        """A class implementing the protocol should pass isinstance check."""
        classifier = MockIntentClassifier()
        assert isinstance(classifier, ProtocolIntentClassifier)

    def test_non_compliant_class_fails_isinstance_check(self) -> None:
        """A class not implementing the protocol should fail isinstance check."""
        not_a_classifier = NonCompliantClassifier()
        assert not isinstance(not_a_classifier, ProtocolIntentClassifier)

    def test_partial_implementation_fails_isinstance_check(self) -> None:
        """A class with wrong method name should fail isinstance check."""
        partial = PartialClassifier()
        assert not isinstance(partial, ProtocolIntentClassifier)

    def test_sync_method_still_passes_isinstance_check(self) -> None:
        """A class with sync method passes isinstance (runtime check is structural).

        Note: Python's runtime protocol checking only verifies attribute presence,
        not whether it's async. This is a limitation of runtime_checkable.
        Static type checkers would catch this issue.
        """
        sync_classifier = SyncClassifier()
        # Runtime check only verifies method exists, not that it's async
        assert isinstance(sync_classifier, ProtocolIntentClassifier)

    def test_wrong_signature_still_passes_isinstance_check(self) -> None:
        """A class with wrong signature passes isinstance (runtime check is structural).

        Note: Python's runtime protocol checking only verifies attribute presence,
        not the full method signature. Static type checkers would catch this.
        """
        wrong_sig = WrongSignatureClassifier()
        # Runtime check only verifies method exists
        assert isinstance(wrong_sig, ProtocolIntentClassifier)


@pytest.mark.unit
class TestMockIntentClassifierImplementation:
    """Test that MockIntentClassifier has all required members."""

    def test_mock_has_classify_intent_method(self) -> None:
        """Mock should have classify_intent method."""
        classifier = MockIntentClassifier()
        assert hasattr(classifier, "classify_intent")
        assert callable(classifier.classify_intent)

    def test_mock_classify_intent_is_async(self) -> None:
        """Mock classify_intent should be async."""
        classifier = MockIntentClassifier()
        assert inspect.iscoroutinefunction(classifier.classify_intent)

    @pytest.mark.asyncio
    async def test_mock_classify_intent_returns_output(self) -> None:
        """Mock should return classification output."""
        classifier = MockIntentClassifier()
        input_data = MockIntentClassificationInput(content="Generate a Python function")

        result = await classifier.classify_intent(input_data)

        assert result is not None
        assert result.success is True
        assert result.intent_category == "code_generation"
        assert result.confidence == 0.95


@pytest.mark.unit
class TestProtocolIntentClassifierImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol_intent_classifier module."""
        from omnibase_spi.protocols.intelligence.protocol_intent_classifier import (
            ProtocolIntentClassifier as DirectProtocolIntentClassifier,
        )

        classifier = MockIntentClassifier()
        assert isinstance(classifier, DirectProtocolIntentClassifier)

    def test_protocol_exports_from_intelligence_module(self) -> None:
        """Protocol should be importable from intelligence module."""
        from omnibase_spi.protocols.intelligence import (
            ProtocolIntentClassifier as IntelligenceProtocolIntentClassifier,
        )

        classifier = MockIntentClassifier()
        assert isinstance(classifier, IntelligenceProtocolIntentClassifier)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.intelligence import (
            ProtocolIntentClassifier as IntelligenceProtocolIntentClassifier,
        )
        from omnibase_spi.protocols.intelligence.protocol_intent_classifier import (
            ProtocolIntentClassifier as DirectProtocolIntentClassifier,
        )

        assert DirectProtocolIntentClassifier is IntelligenceProtocolIntentClassifier

    def test_protocol_exports_from_main_module(self) -> None:
        """Protocol should be importable from main protocols module."""
        from omnibase_spi.protocols import (
            ProtocolIntentClassifier as MainProtocolIntentClassifier,
        )

        classifier = MockIntentClassifier()
        assert isinstance(classifier, MainProtocolIntentClassifier)


@pytest.mark.unit
class TestProtocolIntentClassifierDocumentation:
    """Test that ProtocolIntentClassifier has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolIntentClassifier should have a docstring."""
        assert ProtocolIntentClassifier.__doc__ is not None
        assert len(ProtocolIntentClassifier.__doc__.strip()) > 0

    def test_docstring_mentions_intent_classification(self) -> None:
        """Docstring should mention intent classification purpose."""
        doc = ProtocolIntentClassifier.__doc__ or ""
        assert "intent" in doc.lower()

    def test_docstring_mentions_categories(self) -> None:
        """Docstring should mention intent categories."""
        doc = ProtocolIntentClassifier.__doc__ or ""
        # Should mention at least one of the 9 categories
        categories = [
            "code_generation",
            "debugging",
            "refactoring",
            "testing",
            "documentation",
            "analysis",
            "pattern_learning",
            "quality_assessment",
            "semantic_analysis",
        ]
        assert any(cat in doc for cat in categories)

    def test_classify_intent_method_has_docstring(self) -> None:
        """The classify_intent method should have a docstring."""
        method = getattr(ProtocolIntentClassifier, "classify_intent", None)
        assert method is not None
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0


@pytest.mark.unit
class TestIntentCategories:
    """Test that the protocol documents all 9 intent categories."""

    def test_protocol_documents_original_six_categories(self) -> None:
        """Protocol docstring should document original 6 intent categories."""
        doc = ProtocolIntentClassifier.__doc__ or ""
        original_categories = [
            "code_generation",
            "debugging",
            "refactoring",
            "testing",
            "documentation",
            "analysis",
        ]
        for category in original_categories:
            assert category in doc, f"Missing category: {category}"

    def test_protocol_documents_intelligence_three_categories(self) -> None:
        """Protocol docstring should document intelligence 3 categories."""
        doc = ProtocolIntentClassifier.__doc__ or ""
        intelligence_categories = [
            "pattern_learning",
            "quality_assessment",
            "semantic_analysis",
        ]
        for category in intelligence_categories:
            assert category in doc, f"Missing category: {category}"
