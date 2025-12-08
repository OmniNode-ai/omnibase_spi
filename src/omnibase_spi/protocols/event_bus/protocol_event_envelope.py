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

    The envelope pattern wraps event payloads with metadata (correlation IDs,
    timestamps, routing information) for distributed tracing and event sourcing.

    Type Parameter:
        T: The type of the wrapped event payload.

    Example:
        ```python
        async def handle_user_event(
            envelope: ProtocolEventEnvelope[UserCreatedPayload]
        ) -> None:
            payload = await envelope.get_payload()
            print(f"User created: {payload.user_id}")
        ```
    """

    async def get_payload(self) -> T:
        """Get the wrapped event payload from the envelope.

        Extracts and returns the typed payload contained within this envelope.
        The payload type is determined by the generic type parameter T.

        Returns:
            The unwrapped event payload of type T.

        Raises:
            SPIError: If the payload cannot be extracted or deserialized.
        """
        ...
