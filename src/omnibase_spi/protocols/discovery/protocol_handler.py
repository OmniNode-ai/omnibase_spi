"""
Protocol definition for generic handlers.

This protocol replaces Any type usage when referring to handler objects
by providing a proper protocol interface.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolHandler(Protocol):
    """
    Base protocol for all handlers in the ONEX system.

    This protocol defines the minimal interface that all handlers must implement.
    """

    async def handle(self, *args: Any, **kwargs: Any) -> bool: ...
