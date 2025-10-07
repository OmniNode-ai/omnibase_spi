"""
Protocol interface for advanced text preprocessing.

Defines the contract for sophisticated text preprocessing capabilities
including configurable chunking, overlap handling, and language-aware processing.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_semantic_types import (
        ProtocolPreprocessingInputState,
        ProtocolPreprocessingOutputState,
    )


@runtime_checkable
class ProtocolAdvancedPreprocessor(Protocol):
    """
    Protocol for advanced text preprocessing tools.

    This protocol defines the interface for tools that provide sophisticated
    text preprocessing capabilities with configurable strategies and validation.
    """

    async def process(
        self, input_state: "ProtocolPreprocessingInputState"
    ) -> "ProtocolPreprocessingOutputState":
        """
        Process documents with advanced preprocessing strategies.

        Args:
            input_state: Input state containing documents and configuration

        Returns:
            Output state with processed documents and metadata
        """
        ...
