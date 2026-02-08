"""ContractSessionIndex -- stable pointer wire format.

A lightweight pointer that uniquely identifies a session and allows
resuming or querying its state from persistent storage.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ContractSessionIndex(BaseModel):
    """Stable pointer to a pipeline session for resume and lookup.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        session_id: Unique session identifier.
        ticket_id: Associated ticket (e.g. OMN-1234).
        repo: Repository name or path.
        branch: Git branch at session start.
        created_at_iso: ISO-8601 timestamp when the session was created.
        last_active_iso: ISO-8601 timestamp of last activity.
        state_path: Filesystem path to the persisted state file.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    session_id: str = Field(
        ...,
        description="Unique session identifier.",
    )
    ticket_id: str = Field(
        default="",
        description="Associated ticket (e.g. OMN-1234).",
    )
    repo: str = Field(
        default="",
        description="Repository name or path.",
    )
    branch: str = Field(
        default="",
        description="Git branch at session start.",
    )
    created_at_iso: str = Field(
        default="",
        description="ISO-8601 timestamp when the session was created.",
    )
    last_active_iso: str = Field(
        default="",
        description="ISO-8601 timestamp of last activity.",
    )
    state_path: str = Field(
        default="",
        description="Filesystem path to the persisted state file.",
    )
