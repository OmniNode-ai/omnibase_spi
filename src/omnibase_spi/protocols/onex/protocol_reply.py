"""
Reply Protocol Interface

Protocol interface for standard reply pattern.
Defines the contract for response replies with status, data, and error information.
"""

from typing import TYPE_CHECKING, Literal, Protocol, TypeVar, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.onex.protocol_validation import (
        ProtocolOnexMetadata,
    )
    from omnibase_spi.protocols.types.protocol_core_types import ProtocolDateTime

T = TypeVar("T")
R = TypeVar("R")
LiteralOnexReplyStatus = Literal[
    "success", "partial_success", "failure", "error", "timeout", "validation_error"
]


@runtime_checkable
class ProtocolReply(Protocol):
    """
    Protocol interface for reply pattern.

    All ONEX tools must implement this protocol for response reply handling.
    Provides standardized response wrapping with status and error information.
    """

    async def create_success_reply(
        self,
        data: T,
        correlation_id: UUID | None = None,
        metadata: "ProtocolOnexMetadata | None" = None,
    ) -> R:
        """
        Create a success reply with the given data.

        Args:
            data: The response data to include in the reply.
            correlation_id: Optional UUID for request correlation tracking.
            metadata: Optional metadata about the response.

        Returns:
            R: The created success reply.

        Raises:
            ValidationError: If the data fails validation.
            TypeError: If data is not of an acceptable type.
        """
        ...

    async def create_error_reply(
        self,
        error_message: str,
        error_code: str | None = None,
        error_details: str | None = None,
        correlation_id: UUID | None = None,
        metadata: "ProtocolOnexMetadata | None" = None,
    ) -> R:
        """
        Create an error reply with the given error information.

        Args:
            error_message: Human-readable error message.
            error_code: Optional error code for programmatic handling.
            error_details: Optional additional error details.
            correlation_id: Optional UUID for request correlation tracking.
            metadata: Optional metadata about the response.

        Returns:
            R: The created error reply.

        Raises:
            ValueError: If error_message is empty or None.
            TypeError: If error_message is not a string.
        """
        ...

    async def create_validation_error_reply(
        self,
        validation_errors: list[str],
        correlation_id: UUID | None = None,
        metadata: "ProtocolOnexMetadata | None" = None,
    ) -> R:
        """
        Create a validation error reply with the given errors.

        Args:
            validation_errors: List of validation error messages.
            correlation_id: Optional UUID for request correlation tracking.
            metadata: Optional metadata about the response.

        Returns:
            R: The created validation error reply.

        Raises:
            ValueError: If validation_errors is empty.
            TypeError: If validation_errors is not a list of strings.
        """
        ...

    def extract_data(self, reply: R) -> T | None:
        """
        Extract the data from a reply.

        Args:
            reply: The reply to extract data from.

        Returns:
            T | None: The extracted data if present, None for error replies.

        Raises:
            TypeError: If reply is not of the expected type.
        """
        ...

    async def get_status(self, reply: R) -> "LiteralOnexReplyStatus":
        """
        Get the status from a reply.

        Args:
            reply: The reply to get the status from.

        Returns:
            LiteralOnexReplyStatus: The reply status.

        Raises:
            TypeError: If reply is not of the expected type.
            AttributeError: If reply does not have a status attribute.
        """
        ...

    async def get_error_message(self, reply: R) -> str | None:
        """
        Get the error message from a reply.

        Args:
            reply: The reply to get the error message from.

        Returns:
            str | None: The error message if present.

        Raises:
            TypeError: If reply is not of the expected type.
        """
        ...

    async def get_error_code(self, reply: R) -> str | None:
        """
        Get the error code from a reply.

        Args:
            reply: The reply to get the error code from.

        Returns:
            str | None: The error code if present.

        Raises:
            TypeError: If reply is not of the expected type.
        """
        ...

    async def get_error_details(self, reply: R) -> str | None:
        """
        Get the error details from a reply.

        Args:
            reply: The reply to get the error details from.

        Returns:
            str | None: The error details if present.

        Raises:
            TypeError: If reply is not of the expected type.
        """
        ...

    async def get_correlation_id(self, reply: R) -> UUID | None:
        """
        Get the correlation ID from a reply.

        Args:
            reply: The reply to get the correlation ID from.

        Returns:
            UUID | None: The correlation ID if present.

        Raises:
            TypeError: If reply is not of the expected type.
        """
        ...

    async def get_metadata(self, reply: R) -> "ProtocolOnexMetadata | None":
        """
        Get the metadata from a reply.

        Args:
            reply: The reply to get the metadata from.

        Returns:
            ProtocolOnexMetadata | None: The metadata if present.

        Raises:
            TypeError: If reply is not of the expected type.
        """
        ...

    def is_success(self, reply: R) -> bool:
        """
        Check if a reply indicates success.

        Args:
            reply: The reply to check.

        Returns:
            bool: True if the reply indicates success.

        Raises:
            TypeError: If reply is not of the expected type.
        """
        ...

    def is_error(self, reply: R) -> bool:
        """
        Check if a reply indicates an error.

        Args:
            reply: The reply to check.

        Returns:
            bool: True if the reply indicates an error.

        Raises:
            TypeError: If reply is not of the expected type.
        """
        ...

    async def get_timestamp(self, reply: R) -> "ProtocolDateTime":
        """
        Get the timestamp from a reply.

        Args:
            reply: The reply to get the timestamp from.

        Returns:
            ProtocolDateTime: The reply timestamp.

        Raises:
            TypeError: If reply is not of the expected type.
            AttributeError: If reply does not have a timestamp attribute.
        """
        ...

    async def get_processing_time(self, reply: R) -> float | None:
        """
        Get the processing time from a reply.

        Args:
            reply: The reply to get the processing time from.

        Returns:
            float | None: The processing time in seconds if available.

        Raises:
            TypeError: If reply is not of the expected type.
        """
        ...

    def with_metadata(self, reply: R, metadata: "ProtocolOnexMetadata") -> R:
        """
        Create a new reply with updated metadata.

        Args:
            reply: The original reply.
            metadata: The new metadata to set.

        Returns:
            R: A new reply with the updated metadata.

        Raises:
            ValidationError: If the metadata fails validation.
            TypeError: If reply or metadata is not of the expected type.
        """
        ...

    def is_onex_compliant(self, reply: R) -> bool:
        """
        Check if a reply is ONEX compliant.

        Args:
            reply: The reply to check for compliance.

        Returns:
            bool: True if the reply is ONEX compliant.

        Raises:
            TypeError: If reply is not of the expected type.
        """
        ...

    async def validate_reply(self, reply: R) -> bool:
        """
        Validate a reply's structure and content.

        Args:
            reply: The reply to validate.

        Returns:
            bool: True if the reply is valid.

        Raises:
            ValidationError: If reply structure is malformed and cannot be validated.
            TypeError: If the reply is not of the expected type.
        """
        ...
