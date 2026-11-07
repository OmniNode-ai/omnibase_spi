# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for the ticket store a floor task's ticket is read from, searched in and created in."""

from typing import TYPE_CHECKING, ClassVar, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.services import (
        ModelFloorTicketCreateRequest,
        ModelFloorTicketCreateResult,
        ModelFloorTicketLookupRequest,
        ModelFloorTicketLookupResult,
        ModelFloorTicketSearchRequest,
        ModelFloorTicketSearchResult,
    )


@runtime_checkable
class ProtocolFloorTicketStore(Protocol):
    """Read one ticket, search by a ``Floor key:`` line, or create the ticket of one floor task.

    No call raises for an expected outcome: a ticket that is absent, a refusal and a
    store that cannot answer are each a typed result with their cause. The
    ``synchronous_execution = True`` class-level flag is read by the SPI validator
    to exempt the methods from the async-by-default rule: each call is a
    synchronous request/result exchange.
    """

    synchronous_execution: ClassVar[bool]

    def read(
        self, request: "ModelFloorTicketLookupRequest"
    ) -> "ModelFloorTicketLookupResult":
        """Read the ticket ``request.ticket`` names."""
        ...

    def search_by_floor_key(
        self, request: "ModelFloorTicketSearchRequest"
    ) -> "ModelFloorTicketSearchResult":
        """Return every ticket whose description carries the ``Floor key:`` line of ``request.floor_key``."""
        ...

    def create(
        self, request: "ModelFloorTicketCreateRequest"
    ) -> "ModelFloorTicketCreateResult":
        """Create the ticket of one floor task, or refuse the payload with the cause."""
        ...


__all__ = ["ProtocolFloorTicketStore"]
