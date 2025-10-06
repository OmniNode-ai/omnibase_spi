"""
Protocol for ONEX URI parser utilities.

Provides a clean interface for URI parsing operations without exposing
implementation-specific details. This protocol enables testing and
cross-component URI parsing while maintaining proper architectural boundaries.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue

if TYPE_CHECKING:
    pass


@runtime_checkable
class ProtocolUriParser(Protocol):
    """
    Protocol for ONEX URI parser utilities.

    All implementations must provide a parse method that returns a URI structure.
    This protocol abstracts URI parsing to enable different implementations
    while maintaining a consistent interface.

    Example:
        class MyUriParser(ProtocolUriParser):
            def parse(self, uri_string: str) -> dict[str, ContextValue]:
                ...
    """

    def parse(self, uri_string: str) -> dict[str, "ContextValue"]: ...
