"""
Onex Reply Protocol Interface

Protocol interface for Onex standard reply pattern.
Defines the contract for response replies with status, data, and error information.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from ..protocols.protocol_onex_validation import ModelOnexMetadata


class EnumOnexReplyStatus(str, Enum):
    """Standard Onex reply status values."""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    ERROR = "error"
    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"


class ProtocolOnexReply(ABC):
    """
    Protocol interface for Onex reply pattern.

    All ONEX tools must implement this protocol for response reply handling.
    Provides standardized response wrapping with status and error information.
    """

    @abstractmethod
    def create_success_reply(
        self,
        data: BaseModel,
        correlation_id: Optional[UUID] = None,
        metadata: Optional[ModelOnexMetadata] = None,
    ) -> BaseModel:
        """
        Create a successful Onex reply with data.

        Args:
            data: The response data to be wrapped
            correlation_id: Optional correlation ID for request tracking
            metadata: Additional metadata for the reply

        Returns:
            Onex reply model containing success status and data
        """
        pass

    @abstractmethod
    def create_error_reply(
        self,
        error_message: str,
        error_code: Optional[str] = None,
        error_details: Optional[str] = None,
        correlation_id: Optional[UUID] = None,
        metadata: Optional[ModelOnexMetadata] = None,
    ) -> BaseModel:
        """
        Create an error Onex reply with error information.

        Args:
            error_message: Human-readable error message
            error_code: Optional error code for programmatic handling
            error_details: Additional error details and context
            correlation_id: Optional correlation ID for request tracking
            metadata: Additional metadata for the reply

        Returns:
            Onex reply model containing error status and information
        """
        pass

    @abstractmethod
    def create_validation_error_reply(
        self,
        validation_errors: List[str],
        correlation_id: Optional[UUID] = None,
        metadata: Optional[ModelOnexMetadata] = None,
    ) -> BaseModel:
        """
        Create a validation error Onex reply with validation issues.

        Args:
            validation_errors: List of validation error messages
            correlation_id: Optional correlation ID for request tracking
            metadata: Additional metadata for the reply

        Returns:
            Onex reply model containing validation error status and details
        """
        pass

    @abstractmethod
    def extract_data(self, reply: BaseModel) -> Optional[BaseModel]:
        """
        Extract the data from an Onex reply.

        Args:
            reply: Onex reply containing response data

        Returns:
            The unwrapped response data, None if error reply
        """
        pass

    @abstractmethod
    def get_status(self, reply: BaseModel) -> EnumOnexReplyStatus:
        """
        Get the status from an Onex reply.

        Args:
            reply: Onex reply to extract status from

        Returns:
            The reply status
        """
        pass

    @abstractmethod
    def get_error_message(self, reply: BaseModel) -> Optional[str]:
        """
        Get the error message from an Onex reply.

        Args:
            reply: Onex reply to extract error message from

        Returns:
            The error message if present, None otherwise
        """
        pass

    @abstractmethod
    def get_error_code(self, reply: BaseModel) -> Optional[str]:
        """
        Get the error code from an Onex reply.

        Args:
            reply: Onex reply to extract error code from

        Returns:
            The error code if present, None otherwise
        """
        pass

    @abstractmethod
    def get_error_details(self, reply: BaseModel) -> Optional[str]:
        """
        Get the error details from an Onex reply.

        Args:
            reply: Onex reply to extract error details from

        Returns:
            The error details if present, None otherwise
        """
        pass

    @abstractmethod
    def get_correlation_id(self, reply: BaseModel) -> Optional[UUID]:
        """
        Get the correlation ID from an Onex reply.

        Args:
            reply: Onex reply to extract correlation ID from

        Returns:
            The correlation ID if present, None otherwise
        """
        pass

    @abstractmethod
    def get_metadata(self, reply: BaseModel) -> Optional[ModelOnexMetadata]:
        """
        Get all metadata from an Onex reply.

        Args:
            reply: Onex reply to extract metadata from

        Returns:
            Dictionary containing all reply metadata
        """
        pass

    @abstractmethod
    def is_success(self, reply: BaseModel) -> bool:
        """
        Check if Onex reply indicates success.

        Args:
            reply: Onex reply to check status for

        Returns:
            True if reply indicates success, False otherwise
        """
        pass

    @abstractmethod
    def is_error(self, reply: BaseModel) -> bool:
        """
        Check if Onex reply indicates error.

        Args:
            reply: Onex reply to check status for

        Returns:
            True if reply indicates error, False otherwise
        """
        pass

    @abstractmethod
    def get_timestamp(self, reply: BaseModel) -> datetime:
        """
        Get the creation timestamp from an Onex reply.

        Args:
            reply: Onex reply to extract timestamp from

        Returns:
            The reply creation timestamp
        """
        pass

    @abstractmethod
    def get_processing_time(self, reply: BaseModel) -> Optional[float]:
        """
        Get the processing time from an Onex reply.

        Args:
            reply: Onex reply to extract processing time from

        Returns:
            The processing time in seconds if present, None otherwise
        """
        pass

    @abstractmethod
    def with_metadata(self, reply: BaseModel, metadata: ModelOnexMetadata) -> BaseModel:
        """
        Add metadata to an Onex reply.

        Args:
            reply: Onex reply to add metadata to
            key: Metadata key
            value: Metadata value

        Returns:
            Updated reply with new metadata
        """
        pass

    @abstractmethod
    def is_onex_compliant(self, reply: BaseModel) -> bool:
        """
        Check if reply follows Onex standard compliance.

        Args:
            reply: Onex reply to check compliance for

        Returns:
            True if reply is Onex compliant, False otherwise
        """
        pass

    @abstractmethod
    def validate_reply(self, reply: BaseModel) -> bool:
        """
        Validate an Onex reply for completeness and compliance.

        Args:
            reply: Onex reply to validate

        Returns:
            True if reply is valid, False otherwise
        """
        pass
