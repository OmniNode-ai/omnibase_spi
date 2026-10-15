# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Tests for ProtocolContextSource (OMN-21124).

The protocol is the SPI half of the context-source contract: its ``handle``
takes and returns the core models omnibase_core#1988 introduced
(ModelContextSourceRequest / ModelContextSourceResult). The runtime-checkable
check is structural (a ``handle`` method), but the signature types must come
from omnibase_core — the test pins that import discipline too.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from omnibase_core.enums.enum_context_factor import EnumContextFactor
from omnibase_core.enums.enum_context_source_status import EnumContextSourceStatus
from omnibase_core.models.context.model_context_access import ModelContextAccess
from omnibase_core.models.context.model_context_source_request import (
    ModelContextSourceRequest,
)
from omnibase_core.models.context.model_context_source_result import (
    ModelContextSourceResult,
)
from omnibase_spi.protocols.intelligence.protocol_context_source import (
    ProtocolContextSource,
)


class _FixedSource:
    """A minimal conforming implementation."""

    # The protocol's sync-execution contract flag (see ProtocolEffect's
    # convention): conforming implementations declare it alongside handle.
    synchronous_execution: ClassVar[bool] = True

    def handle(self, request: ModelContextSourceRequest) -> ModelContextSourceResult:
        assert request.revision
        return ModelContextSourceResult(
            status=EnumContextSourceStatus.UNRESOLVED,
        )


class _NotASource:
    """Has no ``handle`` method at all."""

    def read(self) -> None: ...


def _request() -> ModelContextSourceRequest:
    return ModelContextSourceRequest(
        factor=EnumContextFactor.REPO_STATE,
        access=ModelContextAccess(tenant_id="fixture-tenant"),
        revision="fixture-revision",
    )


def test_conforming_source_satisfies_protocol() -> None:
    source = _FixedSource()
    assert isinstance(source, ProtocolContextSource)
    result = source.handle(_request())
    assert result.status is EnumContextSourceStatus.UNRESOLVED


def test_non_conforming_object_does_not_satisfy_protocol() -> None:
    assert not isinstance(_NotASource(), ProtocolContextSource)


def test_signature_types_come_from_omnibase_core() -> None:
    module_path = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "omnibase_spi"
        / "protocols"
        / "intelligence"
        / "protocol_context_source.py"
    )
    source = module_path.read_text()
    assert (
        "from omnibase_core.models.context.model_context_source_request import"
        in source
    )
    assert (
        "from omnibase_core.models.context.model_context_source_result import" in source
    )
    # The SPI must not fork the wire models locally.
    assert "class ModelContextSource" not in source
