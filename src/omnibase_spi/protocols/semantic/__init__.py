"""
Semantic Processing Protocol Interfaces

Protocols for semantic analysis, retrieval, and preprocessing operations
in the ONEX ecosystem. These interfaces enable consistent semantic processing
across different implementations and algorithms.

Key Protocols:
    - ProtocolAdvancedPreprocessor: Interface for advanced text preprocessing
    - ProtocolHybridRetriever: Interface for hybrid semantic retrieval systems

Usage Example:
    from omnibase_spi.protocols.semantic import (
        ProtocolAdvancedPreprocessor,
        ProtocolHybridRetriever
    )

    # Create implementations
    class MyPreprocessor(ProtocolAdvancedPreprocessor):
        async def preprocess(self, text: str) -> dict:
            # Implementation here
            ...
"""

from omnibase_spi.protocols.semantic.protocol_advanced_preprocessor import (
    ProtocolAdvancedPreprocessor,
)
from omnibase_spi.protocols.semantic.protocol_hybrid_retriever import (
    ProtocolHybridRetriever,
)

__all__ = [
    "ProtocolAdvancedPreprocessor",
    "ProtocolHybridRetriever",
]
