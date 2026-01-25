# SPDX-License-Identifier: MIT
# Copyright (c) 2025 OmniNode Team
"""Intelligence protocols for intent classification and analysis.

This module exports protocols related to intelligence operations including
intent classification, pattern recognition, and semantic analysis.

Protocols:
    ProtocolIntentClassifier: Protocol for classifying user intents from text.

Example:
    >>> from omnibase_spi.protocols.intelligence import ProtocolIntentClassifier
    >>>
    >>> def check_compliance(classifier: ProtocolIntentClassifier) -> bool:
    ...     return isinstance(classifier, ProtocolIntentClassifier)
"""

from omnibase_spi.protocols.intelligence.protocol_intent_classifier import (
    ProtocolIntentClassifier,
)

__all__ = [
    "ProtocolIntentClassifier",
]
