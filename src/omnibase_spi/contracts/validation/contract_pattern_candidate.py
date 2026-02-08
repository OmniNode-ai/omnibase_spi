"""ContractPatternCandidate -- pattern submitted for validation.

Represents a code or configuration pattern that has been proposed for
validation before it can be promoted to production.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContractPatternCandidate(BaseModel):
    """A pattern submitted for validation before promotion.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        pattern_id: Unique identifier for this pattern candidate.
        source: Where the pattern originated (e.g. 'agent', 'human', 'template').
        pattern_type: Classification of the pattern (e.g. 'code', 'config', 'contract').
        content: The pattern content (code snippet, config YAML, etc.).
        file_path: File path where the pattern applies (if applicable).
        language: Programming language or format (e.g. 'python', 'yaml').
        metadata: Arbitrary metadata about the pattern.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    pattern_id: str = Field(
        ...,
        description="Unique identifier for this pattern candidate.",
    )
    source: str = Field(
        default="",
        description="Where the pattern originated (e.g. 'agent', 'human').",
    )
    pattern_type: str = Field(
        default="",
        description="Classification of the pattern (e.g. 'code', 'config').",
    )
    content: str = Field(
        default="",
        description="The pattern content (code snippet, config, etc.).",
    )
    file_path: str = Field(
        default="",
        description="File path where the pattern applies.",
    )
    language: str = Field(
        default="",
        description="Programming language or format (e.g. 'python', 'yaml').",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata about the pattern.",
    )
