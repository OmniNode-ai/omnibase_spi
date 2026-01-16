"""
Semantic processing types for ONEX SPI interfaces.

This module defines protocol types for semantic processing operations including
retrieval systems, preprocessing, and natural language processing capabilities.

All types follow the zero-dependency principle and use strong typing with JsonType
from omnibase_core.types for flexible dictionary values.
"""

from typing import Protocol, runtime_checkable

from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolRetrievalInputState(Protocol):
    """
    Protocol for retrieval input state containing query and search parameters.

    This protocol defines the contract for input data to retrieval systems,
    including the query string, search parameters, and configuration options.
    """

    async def query(self) -> str:
        """The search query string.

        Returns:
            The query string to use for search operations.
        """
        ...

    @property
    def search_parameters(self) -> "JsonType":
        """Search configuration parameters as JSON-compatible dictionary.

        Returns:
            Dictionary containing search configuration options.
        """
        ...

    @property
    def filters(self) -> "JsonType | None":
        """Optional filters to apply to search results.

        Returns:
            JSON-compatible dictionary of filter criteria, or None if no filters.
        """
        ...

    @property
    def max_results(self) -> int:
        """Maximum number of results to return.

        Returns:
            The maximum count of results to retrieve.
        """
        ...

    @property
    def offset(self) -> int:
        """Offset for pagination.

        Returns:
            The number of results to skip for pagination.
        """
        ...


@runtime_checkable
class ProtocolRetrievalOutputState(Protocol):
    """
    Protocol for retrieval output state containing search results and metadata.

    This protocol defines the contract for output data from retrieval systems,
    including the retrieved documents, scores, and metadata about the search.
    """

    @property
    def results(self) -> "list[JsonType]":
        """List of retrieved documents with metadata.

        Returns:
            List of JSON-compatible objects representing retrieved documents.
        """
        ...

    @property
    def total_results(self) -> int:
        """Total number of results available.

        Returns:
            The total count of matching results in the search index.
        """
        ...

    async def query(self) -> str:
        """Original query string.

        Returns:
            The query string that was used for this search.
        """
        ...

    @property
    def search_parameters(self) -> "JsonType":
        """Search parameters used for this query.

        Returns:
            JSON-compatible dictionary of the search parameters applied.
        """
        ...

    @property
    def execution_time_ms(self) -> float:
        """Time taken to execute the search in milliseconds.

        Returns:
            The execution time in milliseconds.
        """
        ...

    @property
    def retrieval_method(self) -> str:
        """Method used for retrieval.

        Returns:
            String identifying the retrieval method (e.g., 'hybrid', 'vector', 'keyword').
        """
        ...


@runtime_checkable
class ProtocolPreprocessingInputState(Protocol):
    """
    Protocol for preprocessing input state containing documents and configuration.

    This protocol defines the contract for input data to preprocessing systems,
    including the documents to process and preprocessing configuration.
    """

    @property
    def documents(self) -> "list[JsonType]":
        """List of documents to preprocess.

        Returns:
            List of JSON-compatible objects representing documents to process.
        """
        ...

    @property
    def chunk_size(self) -> int:
        """Size of chunks for document splitting.

        Returns:
            The target size in characters for each document chunk.
        """
        ...

    @property
    def chunk_overlap(self) -> int:
        """Overlap between chunks.

        Returns:
            The number of overlapping characters between adjacent chunks.
        """
        ...

    @property
    def language(self) -> str | None:
        """Language of the documents.

        Returns:
            ISO language code for the documents, or None if unspecified.
        """
        ...

    @property
    def preprocessing_options(self) -> "JsonType":
        """Additional preprocessing options.

        Returns:
            JSON-compatible dictionary of preprocessing configuration options.
        """
        ...


@runtime_checkable
class ProtocolPreprocessingOutputState(Protocol):
    """
    Protocol for preprocessing output state containing processed documents and metadata.

    This protocol defines the contract for output data from preprocessing systems,
    including the processed documents, chunks, and metadata about the preprocessing.
    """

    @property
    def processed_documents(self) -> "list[JsonType]":
        """List of processed documents.

        Returns:
            List of JSON-compatible objects representing processed documents.
        """
        ...

    @property
    def chunks(self) -> "list[JsonType]":
        """List of document chunks.

        Returns:
            List of JSON-compatible objects representing document chunks.
        """
        ...

    @property
    def total_chunks(self) -> int:
        """Total number of chunks generated.

        Returns:
            The count of chunks produced from all documents.
        """
        ...

    @property
    def preprocessing_metadata(self) -> "JsonType":
        """Metadata about the preprocessing process.

        Returns:
            JSON-compatible dictionary containing processing statistics and metadata.
        """
        ...

    @property
    def execution_time_ms(self) -> float:
        """Time taken to execute preprocessing in milliseconds.

        Returns:
            The execution time in milliseconds.
        """
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
