# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Wire-format contracts for ProtocolFloorTicketStore: three requests, three results.

This module MUST NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class ModelFloorTicketLookupRequest(BaseModel):
    """Which ticket to read.

    Attributes:
        ticket: The ticket id.
    """

    model_config = _FROZEN

    ticket: str = Field(..., min_length=1, description="Ticket id.")


class ModelFloorTicketLookupResult(BaseModel):
    """Outcome of reading one ticket.

    Attributes:
        state: ``found`` with the ticket's status, ``missing`` when the store holds
            no such ticket, ``failed`` when the store could not answer.
        ticket: The ticket id; present only for ``found``.
        status: The ticket's status name; present only for ``found``.
        cause: Why the read failed; present only for ``failed``.
        description: The ticket's description, so a reader can check it carries its
            ``Floor key:`` line; only for ``found``, ``None`` when the store gave none.
        project: The ticket's project name, ``None`` when it has none; only for ``found``.
        labels: The ticket's label names; only for ``found``.
        pillar: The ticket's pillar, ``None`` when it has none; only for ``found``.
        has_children: Whether the ticket has child tickets, which makes it an
            umbrella; only for ``found``.
    """

    model_config = _FROZEN

    state: Literal["found", "missing", "failed"] = Field(..., description="Outcome.")
    ticket: str | None = Field(default=None, description="Ticket id when found.")
    status: str | None = Field(default=None, description="Status name when found.")
    cause: str | None = Field(default=None, description="Why the read failed.")
    description: str | None = Field(
        default=None, description="Ticket description when found."
    )
    project: str | None = Field(default=None, description="Project name when found.")
    labels: tuple[str, ...] = Field(default=(), description="Label names when found.")
    pillar: str | None = Field(default=None, description="Pillar when found.")
    has_children: bool = Field(
        default=False, description="Whether the found ticket has child tickets."
    )

    @model_validator(mode="after")
    def _shape_follows_state(self) -> Self:
        if self.state == "found":
            if self.ticket is None or self.status is None or self.cause is not None:
                raise ValueError("found requires a ticket and a status and no cause")
            return self
        if (
            self.description is not None
            or self.project is not None
            or self.labels
            or self.pillar is not None
            or self.has_children
        ):
            raise ValueError(
                "only found carries a description, project, labels, pillar or children"
            )
        if self.state == "missing":
            if (
                self.ticket is not None
                or self.status is not None
                or self.cause is not None
            ):
                raise ValueError("missing carries no ticket, status or cause")
        elif self.cause is None or self.ticket is not None or self.status is not None:
            raise ValueError("failed requires a cause and no ticket or status")
        return self


class ModelFloorTicketSearchRequest(BaseModel):
    """Which floor key to search for.

    Attributes:
        floor_key: The key ``floor:<line_id>:<task_id>`` named by a ``Floor key:`` line.
    """

    model_config = _FROZEN

    floor_key: str = Field(..., min_length=1, description="Floor key to find.")


class ModelFloorTicketSearchResult(BaseModel):
    """Outcome of searching tickets by a ``Floor key:`` line.

    Attributes:
        state: ``answered`` with the matching tickets (possibly none), ``failed`` when
            the store could not answer.
        tickets: Ids of the tickets that carry the key; empty unless ``answered``.
        cause: Why the search failed; present only for ``failed``.
    """

    model_config = _FROZEN

    state: Literal["answered", "failed"] = Field(..., description="Outcome.")
    tickets: tuple[str, ...] = Field(default=(), description="Matching ticket ids.")
    cause: str | None = Field(default=None, description="Why the search failed.")

    @model_validator(mode="after")
    def _shape_follows_state(self) -> Self:
        if self.state == "answered":
            if self.cause is not None:
                raise ValueError("answered carries no cause")
        elif self.cause is None or self.tickets:
            raise ValueError("failed requires a cause and no tickets")
        return self


class ModelFloorTicketCreateRequest(BaseModel):
    """The ticket of one floor task, as the payload compute built it.

    Attributes:
        floor_key: The key ``floor:<line_id>:<task_id>``; the description carries it
            on its ``Floor key:`` line.
        title: Ticket title.
        description: Ticket description, including the ``Floor key:`` line.
        parent: Ticket id of the parent the new ticket sits under.
    """

    model_config = _FROZEN

    floor_key: str = Field(..., min_length=1, description="Floor key of the task.")
    title: str = Field(..., min_length=1, description="Ticket title.")
    description: str = Field(..., min_length=1, description="Ticket description.")
    parent: str = Field(..., min_length=1, description="Parent ticket id.")


class ModelFloorTicketCreateResult(BaseModel):
    """Outcome of creating a floor task's ticket.

    Attributes:
        state: ``created`` with the new ticket, ``refused`` when the store's gate
            refused the payload, ``failed`` when the store could not answer.
        ticket: The new ticket id; present only for ``created``.
        cause: Why it was refused or failed; absent for ``created``.
    """

    model_config = _FROZEN

    state: Literal["created", "refused", "failed"] = Field(..., description="Outcome.")
    ticket: str | None = Field(default=None, description="New ticket id.")
    cause: str | None = Field(default=None, description="Why not created.")

    @model_validator(mode="after")
    def _shape_follows_state(self) -> Self:
        if self.state == "created":
            if self.ticket is None or self.cause is not None:
                raise ValueError("created requires a ticket and no cause")
        elif self.cause is None or self.ticket is not None:
            raise ValueError("refused and failed require a cause and no ticket")
        return self


__all__ = [
    "ModelFloorTicketCreateRequest",
    "ModelFloorTicketCreateResult",
    "ModelFloorTicketLookupRequest",
    "ModelFloorTicketLookupResult",
    "ModelFloorTicketSearchRequest",
    "ModelFloorTicketSearchResult",
]
