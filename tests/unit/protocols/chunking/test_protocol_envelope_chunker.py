# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol conformance tests for ProtocolEnvelopeChunker."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from omnibase_spi.protocols.chunking.protocol_chunkable_envelope import (
    ProtocolChunkableEnvelope,
)
from omnibase_spi.protocols.chunking.protocol_envelope_chunker import (
    ProtocolEnvelopeChunker,
)

if TYPE_CHECKING:
    from omnibase_core.models.chunking.model_chunked_envelope import (
        ModelChunkedEnvelope,
    )


class ConcreteChunker:
    def chunk(
        self,
        envelope: ProtocolChunkableEnvelope,
        max_chunk_size: int,
    ) -> list[ModelChunkedEnvelope]:
        return []

    def reassemble(
        self,
        chunks: list[ModelChunkedEnvelope],
    ) -> ProtocolChunkableEnvelope:
        raise NotImplementedError


@pytest.mark.unit
class TestProtocolEnvelopeChunker:
    def test_concrete_satisfies_protocol(self) -> None:
        assert isinstance(ConcreteChunker(), ProtocolEnvelopeChunker)
