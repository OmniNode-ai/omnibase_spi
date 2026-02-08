"""ContractArtifactPointer -- reference to a produced artifact.

A stable pointer to an artifact (file, PR, commit, etc.) produced by
a pipeline phase, enabling downstream phases to locate it.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContractArtifactPointer(BaseModel):
    """Reference to an artifact produced by a pipeline phase.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        artifact_type: Type of artifact (e.g. 'file', 'pr', 'commit', 'branch').
        name: Human-readable name for the artifact.
        uri: URI or path to the artifact.
        checksum: Optional checksum for integrity verification.
        metadata: Arbitrary metadata about the artifact.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    artifact_type: str = Field(
        ...,
        description="Type of artifact (e.g. 'file', 'pr', 'commit', 'branch').",
    )
    name: str = Field(
        default="",
        description="Human-readable name for the artifact.",
    )
    uri: str = Field(
        default="",
        description="URI or path to the artifact.",
    )
    checksum: str = Field(
        default="",
        description="Optional checksum for integrity verification.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata about the artifact.",
    )
