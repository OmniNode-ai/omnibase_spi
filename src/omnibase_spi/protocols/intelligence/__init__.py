"""Intelligence protocols for intent classification and analysis.

This module exports protocols related to intelligence operations including
intent classification, pattern recognition, semantic analysis, and intent
graph persistence.

Protocols:
    ProtocolIntentClassifier: Protocol for classifying user intents from text.
    ProtocolIntentGraph: Protocol for intent graph persistence operations.
    ProtocolPatternExtractor: Protocol for extracting patterns from content.

Example:
    >>> from omnibase_spi.protocols.intelligence import (
    ...     ProtocolIntentClassifier,
    ...     ProtocolIntentGraph,
    ...     ProtocolPatternExtractor,
    ... )
    >>>
    >>> def check_compliance(classifier: ProtocolIntentClassifier) -> bool:
    ...     return isinstance(classifier, ProtocolIntentClassifier)
"""

from omnibase_spi.protocols.intelligence.protocol_intent_classifier import (
    ProtocolIntentClassifier,
)
from omnibase_spi.protocols.intelligence.protocol_intent_graph import (
    ProtocolIntentGraph,
)
from omnibase_spi.protocols.intelligence.protocol_pattern_extractor import (
    ProtocolPatternExtractor,
)

__all__ = [
    "ProtocolIntentClassifier",
    "ProtocolIntentGraph",
    "ProtocolPatternExtractor",
]
