# SPDX-License-Identifier: MIT
# Copyright (c) 2025 OmniNode Team
"""Intelligence protocols for intent classification and analysis.

This module exports protocols related to intelligence operations including
intent classification, pattern recognition, semantic analysis, and intent
graph persistence.

Protocols:
    ProtocolIntentClassifier: Protocol for classifying user intents from text.
    ProtocolIntentGraph: Protocol for intent graph persistence operations.

Example:
    >>> from omnibase_spi.protocols.intelligence import (
    ...     ProtocolIntentClassifier,
    ...     ProtocolIntentGraph,
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

__all__ = [
    "ProtocolIntentClassifier",
    "ProtocolIntentGraph",
]
