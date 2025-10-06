"""
Protocol for schema exclusion registry functionality.

Defines the interface for managing schema exclusion patterns across
the ONEX ecosystem. This protocol enables consistent handling of
excluded schemas while maintaining proper architectural boundaries.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolSchemaExclusionRegistry(Protocol):
    """
    Canonical protocol for schema exclusion registries shared across nodes.
    Placed in runtime/ per OmniNode Runtime Structure Guidelines: use runtime/ for execution-layer components reused by multiple nodes.
    All schema exclusion logic must conform to this interface.
    """

    def is_schema_file(self, path: str) -> bool:
        """Return True if the given path is a schema file to be excluded, else False."""
        ...
