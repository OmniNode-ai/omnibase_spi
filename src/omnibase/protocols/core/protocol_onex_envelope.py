"""
Onex Envelope Protocol Interface

Protocol interface for Onex standard envelope pattern.
Defines the contract for request envelopes with metadata, correlation IDs, and security context.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from ..models.model_onex_security_context import ModelOnexSecurityContext
from ..protocols.protocol_onex_validation import ModelOnexMetadata


class ProtocolOnexEnvelope(ABC):
    """
    Protocol interface for Onex envelope pattern.

    All ONEX tools must implement this protocol for request envelope handling.
    Provides standardized request wrapping with metadata and security context.
    """

    @abstractmethod
    def create_envelope(
        self,
        payload: BaseModel,
        correlation_id: Optional[UUID] = None,
        security_context: Optional[ModelOnexSecurityContext] = None,
        metadata: Optional[ModelOnexMetadata] = None,
    ) -> BaseModel:
        """
        Create an Onex envelope wrapping the provided payload.

        Args:
            payload: The actual request data to be wrapped
            correlation_id: Optional correlation ID for request tracking
            security_context: Security context information
            metadata: Additional metadata for the request

        Returns:
            Onex envelope model containing wrapped payload and metadata
        """
        pass

    @abstractmethod
    def extract_payload(self, envelope: BaseModel) -> BaseModel:
        """
        Extract the payload from an Onex envelope.

        Args:
            envelope: Onex envelope containing wrapped payload

        Returns:
            The unwrapped payload data
        """
        pass

    @abstractmethod
    def get_correlation_id(self, envelope: BaseModel) -> Optional[UUID]:
        """
        Get the correlation ID from an Onex envelope.

        Args:
            envelope: Onex envelope to extract correlation ID from

        Returns:
            The correlation ID if present, None otherwise
        """
        pass

    @abstractmethod
    def get_security_context(
        self, envelope: BaseModel
    ) -> Optional[ModelOnexSecurityContext]:
        """
        Get the security context from an Onex envelope.

        Args:
            envelope: Onex envelope to extract security context from

        Returns:
            The security context if present, None otherwise
        """
        pass

    @abstractmethod
    def get_metadata(self, envelope: BaseModel) -> Optional[ModelOnexMetadata]:
        """
        Get all metadata from an Onex envelope.

        Args:
            envelope: Onex envelope to extract metadata from

        Returns:
            Dictionary containing all envelope metadata
        """
        pass

    @abstractmethod
    def validate_envelope(self, envelope: BaseModel) -> bool:
        """
        Validate an Onex envelope for completeness and compliance.

        Args:
            envelope: Onex envelope to validate

        Returns:
            True if envelope is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_timestamp(self, envelope: BaseModel) -> datetime:
        """
        Get the creation timestamp from an Onex envelope.

        Args:
            envelope: Onex envelope to extract timestamp from

        Returns:
            The envelope creation timestamp
        """
        pass

    @abstractmethod
    def get_source_tool(self, envelope: BaseModel) -> Optional[str]:
        """
        Get the source tool identifier from an Onex envelope.

        Args:
            envelope: Onex envelope to extract source tool from

        Returns:
            The source tool identifier if present, None otherwise
        """
        pass

    @abstractmethod
    def get_target_tool(self, envelope: BaseModel) -> Optional[str]:
        """
        Get the target tool identifier from an Onex envelope.

        Args:
            envelope: Onex envelope to extract target tool from

        Returns:
            The target tool identifier if present, None otherwise
        """
        pass

    @abstractmethod
    def with_metadata(
        self, envelope: BaseModel, metadata: ModelOnexMetadata
    ) -> BaseModel:
        """
        Add metadata to an Onex envelope.

        Args:
            envelope: Onex envelope to add metadata to
            key: Metadata key
            value: Metadata value

        Returns:
            Updated envelope with new metadata
        """
        pass

    @abstractmethod
    def is_onex_compliant(self, envelope: BaseModel) -> bool:
        """
        Check if envelope follows Onex standard compliance.

        Args:
            envelope: Onex envelope to check compliance for

        Returns:
            True if envelope is Onex compliant, False otherwise
        """
        pass
