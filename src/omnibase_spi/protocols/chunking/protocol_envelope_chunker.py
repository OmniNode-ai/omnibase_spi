# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ProtocolEnvelopeChunker — splits and reassembles chunkable envelopes."""

from typing import Protocol, runtime_checkable

from omnibase_core.models.chunking.model_chunked_envelope import ModelChunkedEnvelope

from omnibase_spi.protocols.chunking.protocol_chunkable_envelope import (
    ProtocolChunkableEnvelope,
)


@runtime_checkable
class ProtocolEnvelopeChunker(Protocol):
    """Protocol for the component that splits and reassembles chunkable envelopes.

    The ChunkingGateway (producer side) delegates to an implementation of this
    protocol. The ReassemblyGateway (consumer side) uses the same implementation
    for reassembly. Chunk payload bytes are treated as opaque; the chunker never
    interprets domain semantics.
    """

    def chunk(
        self,
        envelope: ProtocolChunkableEnvelope,
        max_chunk_size: int,
    ) -> list[ModelChunkedEnvelope]:
        """Split a logical envelope into a list of wire-format chunks.

        Args:
            envelope: The logical envelope to chunk. Must satisfy
                ProtocolChunkableEnvelope (i.e., have to_bytes()).
            max_chunk_size: Maximum number of bytes per chunk payload.

        Returns:
            Ordered list of ModelChunkedEnvelope, one per chunk.
            Concatenating chunk_payload bytes in list order yields the original
            envelope byte representation.

        Raises:
            ValueError: If the envelope cannot be serialized or chunking
                would exceed max_chunk_count policy.
        """
        ...

    def reassemble(
        self,
        chunks: list[ModelChunkedEnvelope],
    ) -> ProtocolChunkableEnvelope:
        """Reassemble a list of chunks into the original logical envelope.

        Args:
            chunks: All chunks for a single chunk series. May be in any order;
                the chunker sorts by chunk_index before concatenating.

        Returns:
            The reconstructed logical envelope.

        Raises:
            ValueError: If chunks are incomplete, checksums fail, or
                deserialization fails.
        """
        ...
