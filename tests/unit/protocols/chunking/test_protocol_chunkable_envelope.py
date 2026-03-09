"""Protocol conformance tests for ProtocolChunkableEnvelope."""

import pytest

from omnibase_spi.protocols.chunking.protocol_chunkable_envelope import (
    ProtocolChunkableEnvelope,
)


class ConcreteChunkable:
    """Minimal conforming implementation for protocol check."""

    def to_bytes(self) -> bytes:
        return b"payload"

    @classmethod
    def from_bytes(cls, data: bytes) -> "ConcreteChunkable":  # noqa: ARG003
        return cls()


@pytest.mark.unit
class TestProtocolChunkableEnvelope:
    def test_concrete_satisfies_protocol(self) -> None:
        assert isinstance(ConcreteChunkable(), ProtocolChunkableEnvelope)

    def test_missing_to_bytes_fails(self) -> None:
        class Missing:
            @classmethod
            def from_bytes(cls, data: bytes) -> "Missing":  # noqa: ARG003
                return cls()

        assert not isinstance(Missing(), ProtocolChunkableEnvelope)

    def test_missing_from_bytes_fails(self) -> None:
        class Missing:
            def to_bytes(self) -> bytes:
                return b""

        assert not isinstance(Missing(), ProtocolChunkableEnvelope)
