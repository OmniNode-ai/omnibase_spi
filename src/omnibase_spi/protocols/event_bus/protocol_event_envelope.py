"""
Protocol for Event Envelope

Defines the minimal interface that mixins need from ModelEventEnvelope
to break circular import dependencies.
"""

from typing import Generic, Protocol, TypeVar, runtime_checkable

T = TypeVar("T", covariant=True)


@runtime_checkable
class ProtocolEventEnvelope(Protocol, Generic[T]):
    """
    Protocol defining the minimal interface for event envelopes.

    This protocol allows mixins to type-hint envelope parameters without
    importing the concrete ModelEventEnvelope class, breaking circular dependencies.
    """

    async def get_payload(self) -> T:
        """Get the wrapped event payload."""
        ...
