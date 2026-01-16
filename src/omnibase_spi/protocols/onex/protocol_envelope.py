"""
Envelope Protocol Interface

Protocol interface for standard envelope pattern.
Defines the contract for request envelopes with metadata, correlation IDs, and security context.
"""

from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.onex.protocol_validation import (
    ProtocolOnexMetadata,
    ProtocolOnexSecurityContext,
)

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ProtocolDateTime

T = TypeVar("T")
E = TypeVar("E")


@runtime_checkable
class ProtocolEnvelope(Protocol):
    """
    Protocol interface for envelope pattern.

    All ONEX tools must implement this protocol for request envelope handling.
    Provides standardized request wrapping with metadata and security context.
    """

    async def create_envelope(
        self,
        payload: T,
        correlation_id: UUID | None = None,
        security_context: "ProtocolOnexSecurityContext | None" = None,
        metadata: "ProtocolOnexMetadata | None" = None,
    ) -> E:
        """
        Create a new envelope wrapping the given payload.

        Args:
            payload: The data to wrap in the envelope.
            correlation_id: Optional UUID for request correlation tracking.
            security_context: Optional security context for authentication.
            metadata: Optional metadata about the request origin.

        Returns:
            E: The created envelope containing the payload.

        Raises:
            ValidationError: If the payload fails validation.
            TypeError: If payload is not of an acceptable type.
        """
        ...

    async def extract_payload(self, envelope: E) -> T:
        """
        Extract the payload from an envelope.

        Args:
            envelope: The envelope to extract the payload from.

        Returns:
            T: The extracted payload data.

        Raises:
            ValueError: If the envelope is invalid or has no payload.
            TypeError: If the envelope is not of the expected type.
        """
        ...

    async def get_correlation_id(self, envelope: E) -> UUID | None:
        """
        Get the correlation ID from an envelope.

        Args:
            envelope: The envelope to get the correlation ID from.

        Returns:
            UUID | None: The correlation ID if present, None otherwise.

        Raises:
            TypeError: If the envelope is not of the expected type.
        """
        ...

    async def get_security_context(
        self, envelope: E
    ) -> "ProtocolOnexSecurityContext | None":
        """
        Get the security context from an envelope.

        Args:
            envelope: The envelope to get the security context from.

        Returns:
            ProtocolOnexSecurityContext | None: The security context if present.

        Raises:
            TypeError: If the envelope is not of the expected type.
        """
        ...

    async def get_metadata(self, envelope: E) -> "ProtocolOnexMetadata | None":
        """
        Get the metadata from an envelope.

        Args:
            envelope: The envelope to get the metadata from.

        Returns:
            ProtocolOnexMetadata | None: The metadata if present.

        Raises:
            TypeError: If the envelope is not of the expected type.
        """
        ...

    async def validate_envelope(self, envelope: E) -> bool:
        """
        Validate an envelope's structure and content.

        Args:
            envelope: The envelope to validate.

        Returns:
            bool: True if the envelope is valid, False otherwise.

        Raises:
            ValidationError: If envelope structure is malformed and cannot be validated.
            TypeError: If the envelope is not of the expected type.
        """
        ...

    async def get_timestamp(self, envelope: E) -> "ProtocolDateTime":
        """
        Get the creation timestamp from an envelope.

        Args:
            envelope: The envelope to get the timestamp from.

        Returns:
            ProtocolDateTime: The envelope creation timestamp.

        Raises:
            ValueError: If the envelope has no timestamp or timestamp is invalid.
            TypeError: If the envelope is not of the expected type.
        """
        ...

    async def get_source_tool(self, envelope: E) -> str | None:
        """
        Get the source tool identifier from an envelope.

        Args:
            envelope: The envelope to get the source tool from.

        Returns:
            str | None: The source tool identifier if present.

        Raises:
            TypeError: If the envelope is not of the expected type.
        """
        ...

    async def get_target_tool(self, envelope: E) -> str | None:
        """
        Get the target tool identifier from an envelope.

        Args:
            envelope: The envelope to get the target tool from.

        Returns:
            str | None: The target tool identifier if present.

        Raises:
            TypeError: If the envelope is not of the expected type.
        """
        ...

    def with_metadata(self, envelope: E, metadata: "ProtocolOnexMetadata") -> E:
        """
        Create a new envelope with updated metadata.

        Args:
            envelope: The original envelope.
            metadata: The new metadata to set.

        Returns:
            E: A new envelope with the updated metadata.

        Raises:
            ValidationError: If the metadata fails validation.
            TypeError: If envelope or metadata is not of the expected type.
        """
        ...

    def is_onex_compliant(self, envelope: E) -> bool:
        """
        Check if an envelope is ONEX compliant.

        Args:
            envelope: The envelope to check for compliance.

        Returns:
            bool: True if the envelope is ONEX compliant, False otherwise.

        Raises:
            TypeError: If the envelope is not of the expected type.
        """
        ...
