"""
Semantic processing types for ONEX SPI interfaces.

This module defines protocol types for semantic processing operations including
retrieval systems, preprocessing, and natural language processing capabilities.

All types follow the zero-dependency principle and use strong typing without Any.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolRetrievalInputState(Protocol):
    """
    Protocol for retrieval input state containing query and search parameters.

    This protocol defines the contract for input data to retrieval systems,
    including the query string, search parameters, and configuration options.
    """

    async def query(self) -> str:
        """The search query string."""
        ...

    @property
    def search_parameters(self) -> dict[str, Any]:
        """Search configuration parameters."""
        ...

    @property
    def filters(self) -> dict[str, Any] | None:
        """Optional filters to apply to search results."""
        ...

    @property
    def max_results(self) -> int:
        """Maximum number of results to return."""
        ...

    @property
    def offset(self) -> int:
        """Offset for pagination."""
        ...


@runtime_checkable
class ProtocolRetrievalOutputState(Protocol):
    """
    Protocol for retrieval output state containing search results and metadata.

    This protocol defines the contract for output data from retrieval systems,
    including the retrieved documents, scores, and metadata about the search.
    """

    @property
    def results(self) -> list[dict[str, Any]]:
        """List of retrieved documents with metadata."""
        ...

    @property
    def total_results(self) -> int:
        """Total number of results available."""
        ...

    async def query(self) -> str:
        """Original query string."""
        ...

    @property
    def search_parameters(self) -> dict[str, Any]:
        """Search parameters used."""
        ...

    @property
    def execution_time_ms(self) -> float:
        """Time taken to execute the search in milliseconds."""
        ...

    @property
    def retrieval_method(self) -> str:
        """Method used for retrieval (e.g., 'hybrid', 'vector', 'keyword')."""
        ...


@runtime_checkable
class ProtocolPreprocessingInputState(Protocol):
    """
    Protocol for preprocessing input state containing documents and configuration.

    This protocol defines the contract for input data to preprocessing systems,
    including the documents to process and preprocessing configuration.
    """

    @property
    def documents(self) -> list[dict[str, Any]]:
        """List of documents to preprocess."""
        ...

    @property
    def chunk_size(self) -> int:
        """Size of chunks for document splitting."""
        ...

    @property
    def chunk_overlap(self) -> int:
        """Overlap between chunks."""
        ...

    @property
    def language(self) -> str | None:
        """Language of the documents."""
        ...

    @property
    def preprocessing_options(self) -> dict[str, Any]:
        """Additional preprocessing options."""
        ...


@runtime_checkable
class ProtocolPreprocessingOutputState(Protocol):
    """
    Protocol for preprocessing output state containing processed documents and metadata.

    This protocol defines the contract for output data from preprocessing systems,
    including the processed documents, chunks, and metadata about the preprocessing.
    """

    @property
    def processed_documents(self) -> list[dict[str, Any]]:
        """List of processed documents."""
        ...

    @property
    def chunks(self) -> list[dict[str, Any]]:
        """List of document chunks."""
        ...

    @property
    def total_chunks(self) -> int:
        """Total number of chunks generated."""
        ...

    @property
    def preprocessing_metadata(self) -> dict[str, Any]:
        """Metadata about the preprocessing process."""
        ...

    @property
    def execution_time_ms(self) -> float:
        """Time taken to execute preprocessing in milliseconds."""
        ...


# Type aliases for backward compatibility and convenience
RetrievalInputState = ProtocolRetrievalInputState
RetrievalOutputState = ProtocolRetrievalOutputState
PreprocessingInputState = ProtocolPreprocessingInputState
PreprocessingOutputState = ProtocolPreprocessingOutputState

__all__ = [
    "PreprocessingInputState",
    "PreprocessingOutputState",
    "ProtocolPreprocessingInputState",
    "ProtocolPreprocessingOutputState",
    "ProtocolRetrievalInputState",
    "ProtocolRetrievalOutputState",
    "RetrievalInputState",
    "RetrievalOutputState",
]
