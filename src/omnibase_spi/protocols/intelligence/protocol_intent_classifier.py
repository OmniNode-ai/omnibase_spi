"""Protocol for intent classification operations.

This module defines the protocol for classifying user intents from text content.
Implementations may use various techniques (TF-IDF, LLM-based, etc.).

Supported Intent Categories (9 total):
- Original 6: code_generation, debugging, refactoring, testing, documentation, analysis
- Intelligence 3: pattern_learning, quality_assessment, semantic_analysis

Example:
    >>> class MyClassifier:
    ...     async def classify_intent(
    ...         self, input_data: ModelIntentClassificationInput
    ...     ) -> ModelIntentClassificationOutput:
    ...         # Implementation here
    ...         ...
    >>>
    >>> # Check protocol compliance
    >>> assert isinstance(MyClassifier(), ProtocolIntentClassifier)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.intelligence import (
        ModelIntentClassificationInput,
        ModelIntentClassificationOutput,
    )

__all__ = ["ProtocolIntentClassifier"]


@runtime_checkable
class ProtocolIntentClassifier(Protocol):
    """Protocol for intent classification operations.

    Defines the interface for classifying user intents from text content.
    Implementations should analyze input text and return classification results
    with confidence scores.

    The protocol supports 9 intent categories:
    - code_generation: Requests to generate new code
    - debugging: Requests to fix errors or investigate issues
    - refactoring: Requests to improve existing code structure
    - testing: Requests related to tests
    - documentation: Requests for documentation
    - analysis: Requests to analyze or explain code
    - pattern_learning: Requests to learn from patterns
    - quality_assessment: Requests to assess code quality
    - semantic_analysis: Requests for semantic understanding

    Example:
        >>> async def example():
        ...     classifier: ProtocolIntentClassifier = get_classifier()
        ...     result = await classifier.classify_intent(input_data)
        ...     print(f"Intent: {result.intent_category}, Confidence: {result.confidence}")
    """

    async def classify_intent(
        self,
        input_data: ModelIntentClassificationInput,
    ) -> ModelIntentClassificationOutput:
        """Classify user intent from input data.

        Analyzes the content in input_data and determines the most likely
        intent category with confidence scoring.

        Args:
            input_data: Input containing content to classify and optional context.
                Contains fields: content (str), correlation_id (UUID | None),
                context (IntentContextDict).

        Returns:
            Classification result containing:
                - success: Whether classification succeeded
                - intent_category: Primary classified intent
                - confidence: Confidence score (0.0 to 1.0)
                - secondary_intents: Additional detected intents
                - metadata: Classification metadata

        Raises:
            May raise implementation-specific exceptions for invalid input
            or classification failures.
        """
        ...
