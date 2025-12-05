"""
Onex Envelope Protocol Interface

Protocol interface for Onex standard envelope pattern.
Defines the contract for request envelopes with metadata, correlation IDs, and security context.
"""

from datetime import datetime
from typing import Protocol, TypeVar, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.onex.protocol_onex_validation import (
    ProtocolOnexMetadata,
    ProtocolOnexSecurityContext,
)

T = TypeVar("T")
E = TypeVar("E")


@runtime_checkable
class ProtocolOnexEnvelope(Protocol):
    """
    Protocol interface for Onex envelope pattern.

    All ONEX tools must implement this protocol for request envelope handling.
    Provides standardized request wrapping with metadata and security context.
    """

    async def create_envelope(
        self,
        payload: T,
        correlation_id: UUID | None = None,
        security_context: "ProtocolOnexSecurityContext | None" = None,
        metadata: "ProtocolOnexMetadata | None" = None,
    ) -> E: ...

    async def extract_payload(self, envelope: E) -> T: ...

    async def get_correlation_id(self, envelope: E) -> UUID | None: ...

    async def get_security_context(
        self, envelope: E
    ) -> "ProtocolOnexSecurityContext | None": ...

    async def get_metadata(self, envelope: E) -> "ProtocolOnexMetadata | None": ...

    async def validate_envelope(self, envelope: E) -> bool: ...

    async def get_timestamp(self, envelope: E) -> datetime: ...

    async def get_source_tool(self, envelope: E) -> str | None: ...

    async def get_target_tool(self, envelope: E) -> str | None: ...

    def with_metadata(self, envelope: E, metadata: "ProtocolOnexMetadata") -> E: ...

    def is_onex_compliant(self, envelope: E) -> bool: ...
