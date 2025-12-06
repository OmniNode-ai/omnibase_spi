"""
Onex Reply Protocol Interface

Protocol interface for Onex standard reply pattern.
Defines the contract for response replies with status, data, and error information.
"""

from typing import TYPE_CHECKING, Literal, Protocol, TypeVar, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.onex.protocol_onex_validation import (
        ProtocolOnexMetadata,
    )
    from omnibase_spi.protocols.types.protocol_core_types import ProtocolDateTime

T = TypeVar("T")
R = TypeVar("R")
LiteralOnexReplyStatus = Literal[
    "success", "partial_success", "failure", "error", "timeout", "validation_error"
]


@runtime_checkable
class ProtocolOnexReply(Protocol):
    """
    Protocol interface for Onex reply pattern.

    All ONEX tools must implement this protocol for response reply handling.
    Provides standardized response wrapping with status and error information.
    """

    async def create_success_reply(
        self,
        data: T,
        correlation_id: UUID | None = None,
        metadata: "ProtocolOnexMetadata | None" = None,
    ) -> R: ...

    async def create_error_reply(
        self,
        error_message: str,
        error_code: str | None = None,
        error_details: str | None = None,
        correlation_id: UUID | None = None,
        metadata: "ProtocolOnexMetadata | None" = None,
    ) -> R: ...

    async def create_validation_error_reply(
        self,
        validation_errors: list[str],
        correlation_id: UUID | None = None,
        metadata: "ProtocolOnexMetadata | None" = None,
    ) -> R: ...

    def extract_data(self, reply: R) -> T | None: ...

    async def get_status(self, reply: R) -> "LiteralOnexReplyStatus": ...

    async def get_error_message(self, reply: R) -> str | None: ...

    async def get_error_code(self, reply: R) -> str | None: ...

    async def get_error_details(self, reply: R) -> str | None: ...

    async def get_correlation_id(self, reply: R) -> UUID | None: ...

    async def get_metadata(self, reply: R) -> "ProtocolOnexMetadata | None": ...

    def is_success(self, reply: R) -> bool: ...

    def is_error(self, reply: R) -> bool: ...

    async def get_timestamp(self, reply: R) -> "ProtocolDateTime": ...

    async def get_processing_time(self, reply: R) -> float | None: ...

    def with_metadata(self, reply: R, metadata: "ProtocolOnexMetadata") -> R: ...

    def is_onex_compliant(self, reply: R) -> bool: ...

    async def validate_reply(self, reply: R) -> bool: ...
