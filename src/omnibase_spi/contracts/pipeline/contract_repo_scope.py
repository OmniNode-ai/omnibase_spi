"""ContractRepoScope -- repo + path glob scope.

Defines the scope of a pipeline operation in terms of which repository
and which file paths within it are affected.

This contract must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ContractRepoScope(BaseModel):
    """Repository and path scope for a pipeline operation.

    Attributes:
        schema_version: Wire-format version for forward compatibility.
        repo: Repository name (e.g. 'omnibase_spi').
        path_globs: File path glob patterns that define the scope.
        branch: Git branch to scope to (empty = any).
        exclude_globs: File path glob patterns to exclude.
    """

    model_config = {"frozen": True, "extra": "allow"}

    schema_version: str = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    repo: str = Field(
        ...,
        description="Repository name (e.g. 'omnibase_spi').",
    )
    path_globs: list[str] = Field(
        default_factory=list,
        description="File path glob patterns that define the scope.",
    )
    branch: str = Field(
        default="",
        description="Git branch to scope to (empty = any).",
    )
    exclude_globs: list[str] = Field(
        default_factory=list,
        description="File path glob patterns to exclude.",
    )
