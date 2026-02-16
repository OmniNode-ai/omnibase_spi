"""ContractAttachment -- file or data attachment for delegation responses.

Represents a single attachment (file, image, data blob) included in a
delegated response.  Used by :class:`ContractDelegatedResponse` to carry
non-textual output alongside rendered Markdown.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ContractAttachment(BaseModel):
    """A file or data attachment accompanying a delegation response.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        filename: Original filename of the attachment.
        content_type: MIME type of the attachment (e.g. 'image/png',
            'application/json').
        content_base64: Base64-encoded content of the attachment.
            Empty string when content is provided out-of-band.
        size_bytes: Size of the decoded content in bytes.
        description: Human-readable description of the attachment.
        extensions: Escape hatch for forward-compatible extension data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    filename: str = Field(
        ...,
        min_length=1,
        description="Original filename of the attachment.",
    )
    content_type: str = Field(
        default="application/octet-stream",
        description=(
            "MIME type of the attachment " "(e.g. 'image/png', 'application/json')."
        ),
    )
    content_base64: str = Field(
        default="",
        description=(
            "Base64-encoded content of the attachment.  "
            "Empty string when content is provided out-of-band."
        ),
    )
    size_bytes: int = Field(
        default=0,
        ge=0,
        description="Size of the decoded content in bytes.",
    )
    description: str = Field(
        default="",
        description="Human-readable description of the attachment.",
    )
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Escape hatch for forward-compatible extension data.",
    )
