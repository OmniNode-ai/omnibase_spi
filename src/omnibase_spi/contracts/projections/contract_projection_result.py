"""ContractProjectionResult -- result wire format for projection writes.

Represents the outcome of a synchronous projection write operation
as returned by ``ProtocolNodeProjectionEffect.execute()``.

This module MUST NOT import from omnibase_core, omnibase_infra, or
omniclaude.  It contains only wire-format data; all business logic lives
in the runtime layer.

Architecture Context:
    ``ProtocolNodeProjectionEffect.execute()`` writes a projection to the
    persistence layer synchronously before returning to the ONEX runtime.
    The runtime inspects this contract to determine whether to proceed
    with the Kafka publish:

    - ``success=True``: projection persisted; runtime publishes to Kafka.
    - ``success=False``: no-op (e.g. sequence already applied); skip publish.
    - Failure: ``execute()`` raises ``ProjectorError`` — it NEVER returns
      ``success=False`` for infrastructure failures.

Related:
    - OMN-2508: ProtocolNodeProjectionEffect as synchronous ProtocolEffect
    - OMN-2460: ModelProjectionIntent (input side of the same boundary)
    - omnibase_spi.exceptions.ProjectorError: raised on persistence failure
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ContractProjectionResult(BaseModel):
    """Wire-format result of a synchronous projection write operation.

    Returned by ``ProtocolNodeProjectionEffect.execute()`` when the write
    completes without raising an exception.

    Design Principles:
        - **Frozen**: Instances are immutable after construction.
        - **Raise on failure**: Infrastructure failures are signalled via
          ``ProjectorError``, not via a ``success=False`` result.  The
          ``success`` field is reserved for non-error no-op writes (e.g.
          idempotent sequence-already-applied skips).
        - **Minimal surface**: Only the fields strictly required by the
          runtime are included here.

    Attributes:
        success: ``True`` when the projection was written (or idempotently
            accepted) without error.  ``False`` for valid no-op writes.
        artifact_ref: Opaque reference to the persisted projection artifact.
            Format is implementation-defined (e.g. a database primary key,
            an S3 object key, or a content-addressable hash).  ``None``
            when ``success`` is ``False`` or when the implementation does
            not assign a stable reference.
        error: Human-readable description of the problem when ``success``
            is ``False`` and no exception was raised.  ``None`` on success.

    Example -- success::

        result = effect.execute(intent)
        assert result.success
        publish_to_kafka(result.artifact_ref)

    Example -- idempotent skip (no-op, not an error)::

        result = ContractProjectionResult(
            success=False,
            artifact_ref=None,
            error="Sequence already applied; skipped.",
        )

    Note:
        ``ProtocolNodeProjectionEffect.execute()`` MUST raise
        ``ProjectorError`` on infrastructure failure.  Returning
        ``success=False`` is reserved for semantically valid non-writes.
    """

    # extra="allow": Forward-compat policy — unknown fields from newer upstream
    # versions are accepted and accessible via __pydantic_extra__ without breaking
    # existing consumers. Callers MUST NOT rely on extra fields for control flow.
    # WARNING: Misspelled field names (e.g., artfact_ref=...) are silently accepted
    # as extra fields rather than raising a ValidationError. Use model_validate()
    # with strict=True during testing to catch field-name typos early.
    model_config = {"frozen": True, "extra": "allow", "from_attributes": True}

    schema_version: Literal["1.0"] = Field(
        default="1.0",
        description="Wire-format version for forward compatibility.",
    )
    success: bool = Field(
        ...,
        description=(
            "True when the projection was written or idempotently accepted. "
            "False for semantically valid no-op writes."
        ),
    )
    artifact_ref: str | None = Field(
        default=None,
        description=(
            "Opaque reference to the persisted projection artifact. "
            "None when success is False or the implementation does not "
            "assign a stable reference."
        ),
    )
    error: str | None = Field(
        default=None,
        description=(
            "Human-readable error description when success is False. None on success."
        ),
    )
