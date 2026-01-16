"""
Reply Protocol Interface

Protocol interface for standard reply pattern.
Defines the contract for response replies with status, data, and error information.
"""

from typing import TYPE_CHECKING, Literal, Protocol, TypeVar, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.onex.protocol_validation import (
        ProtocolMetadata,
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
        metadata: "ProtocolMetadata | None" = None,
    ) -> R:
        """
        Create a success reply with the given data.

        Args:
            data: The response data to include in the reply.
            correlation_id: Optional UUID for request correlation tracking.
            metadata: Optional metadata about the response.

        Returns:
            R: The created success reply.
        """
        ...

    async def create_error_reply(
        self,
        error_message: str,
        error_code: str | None = None,
        error_details: str | None = None,
        correlation_id: UUID | None = None,
        metadata: "ProtocolMetadata | None" = None,
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
        """
        ...

    async def create_validation_error_reply(
        self,
        validation_errors: list[str],
        correlation_id: UUID | None = None,
        metadata: "ProtocolMetadata | None" = None,
    ) -> R:
        """
        Create a validation error reply with the given errors.

        Args:
            validation_errors: List of validation error messages.
            correlation_id: Optional UUID for request correlation tracking.
            metadata: Optional metadata about the response.

        Returns:
            R: The created validation error reply.
        """
        ...

    def extract_data(self, reply: R) -> T | None:
        """
        Extract the data from a reply.

        Args:
            reply: The reply to extract data from.

        Returns:
            T | None: The extracted data if present, None for error replies.
        """
        ...

    async def get_status(self, reply: R) -> "LiteralOnexReplyStatus":
        """
        Get the status from a reply.

        Args:
            reply: The reply to get the status from.

        Returns:
            LiteralOnexReplyStatus: The reply status.
        """
        ...

    async def get_error_message(self, reply: R) -> str | None:
        """
        Get the error message from a reply.

        Args:
            reply: The reply to get the error message from.

        Returns:
            str | None: The error message if present.
        """
        ...

    async def get_error_code(self, reply: R) -> str | None:
        """
        Get the error code from a reply.

        Args:
            reply: The reply to get the error code from.

        Returns:
            str | None: The error code if present.
        """
        ...

    async def get_error_details(self, reply: R) -> str | None:
        """
        Get the error details from a reply.

        Args:
            reply: The reply to get the error details from.

        Returns:
            str | None: The error details if present.
        """
        ...

    async def get_correlation_id(self, reply: R) -> UUID | None:
        """
        Get the correlation ID from a reply.

        Args:
            reply: The reply to get the correlation ID from.

        Returns:
            UUID | None: The correlation ID if present.
        """
        ...

    async def get_metadata(self, reply: R) -> "ProtocolMetadata | None":
        """
        Get the metadata from a reply.

        Args:
            reply: The reply to get the metadata from.

        Returns:
            ProtocolMetadata | None: The metadata if present.
        """
        ...

    def is_success(self, reply: R) -> bool:
        """
        Check if a reply indicates success.

        Args:
            reply: The reply to check.

        Returns:
            bool: True if the reply indicates success.
        """
        ...

    def is_error(self, reply: R) -> bool:
        """
        Check if a reply indicates an error.

        Args:
            reply: The reply to check.

        Returns:
            bool: True if the reply indicates an error.
        """
        ...

    async def get_timestamp(self, reply: R) -> "ProtocolDateTime":
        """
        Get the timestamp from a reply.

        Args:
            reply: The reply to get the timestamp from.

        Returns:
            ProtocolDateTime: The reply timestamp.
        """
        ...

    async def get_processing_time(self, reply: R) -> float | None:
        """
        Get the processing time from a reply.

        Args:
            reply: The reply to get the processing time from.

        Returns:
            float | None: The processing time in seconds if available.
        """
        ...

    def with_metadata(self, reply: R, metadata: "ProtocolMetadata") -> R:
        """
        Create a new reply with updated metadata.

        Args:
            reply: The original reply.
            metadata: The new metadata to set.

        Returns:
            R: A new reply with the updated metadata.
        """
        ...

    def is_onex_compliant(self, reply: R) -> bool:
        """
        Check if a reply is ONEX compliant.

        Args:
            reply: The reply to check for compliance.

        Returns:
            bool: True if the reply is ONEX compliant.
        """
        ...

    async def validate_reply(self, reply: R) -> bool:
        """
        Validate a reply's structure and content.

        Args:
            reply: The reply to validate.

        Returns:
            bool: True if the reply is valid.
        """
        ...
