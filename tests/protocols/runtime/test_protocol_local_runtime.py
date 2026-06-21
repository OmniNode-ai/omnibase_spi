# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Conformance tests for the OMN-13443 local-runtime protocols.

Validates the five local-runtime protocols relocated from
``omnibase_infra.protocols`` into ``omnibase_spi.protocols.runtime``:

- ``ProtocolLocalRuntimeBus`` (+ ``UnsubscribeCallback`` alias)
- ``ProtocolLocalRuntimeMessage``
- ``ProtocolLocalRuntimeCallableTarget``
- ``ProtocolLocalRuntimePayloadModel``
- ``ProtocolLocalRuntimeDumpModel``

Each is ``@runtime_checkable`` and structurally typed (zero ``omnibase``
runtime dependencies beyond the intra-package ``bus -> message`` reference).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

import pytest

from omnibase_spi.protocols.runtime.protocol_local_runtime_bus import (
    ProtocolLocalRuntimeBus,
    UnsubscribeCallback,
)
from omnibase_spi.protocols.runtime.protocol_local_runtime_callable_target import (
    ProtocolLocalRuntimeCallableTarget,
)
from omnibase_spi.protocols.runtime.protocol_local_runtime_dump_model import (
    ProtocolLocalRuntimeDumpModel,
)
from omnibase_spi.protocols.runtime.protocol_local_runtime_message import (
    ProtocolLocalRuntimeMessage,
)
from omnibase_spi.protocols.runtime.protocol_local_runtime_payload_model import (
    ProtocolLocalRuntimePayloadModel,
)


@pytest.mark.unit
def test_message_accepts_object_with_value() -> None:
    class _Msg:
        value: object = b"payload"

    assert isinstance(_Msg(), ProtocolLocalRuntimeMessage)


@pytest.mark.unit
def test_callable_target_accepts_object_with_handle() -> None:
    class _Target:
        def handle(self, *args: object, **kwargs: object) -> object:
            return None

    assert isinstance(_Target(), ProtocolLocalRuntimeCallableTarget)

    class _Bad:
        pass

    assert not isinstance(_Bad(), ProtocolLocalRuntimeCallableTarget)


@pytest.mark.unit
def test_payload_model_accepts_object_with_correlation_id_and_dump() -> None:
    class _Payload:
        correlation_id: object = "abc"

        def model_dump_json(self) -> str:
            return "{}"

    assert isinstance(_Payload(), ProtocolLocalRuntimePayloadModel)


@pytest.mark.unit
def test_dump_model_accepts_object_with_model_dump() -> None:
    class _Dump:
        def model_dump(self, *, mode: str) -> object:
            return {}

    assert isinstance(_Dump(), ProtocolLocalRuntimeDumpModel)


@pytest.mark.unit
def test_bus_accepts_structurally_compliant_implementation() -> None:
    async def _unsub() -> None:
        return None

    class _Bus:
        async def start(self) -> None:
            return None

        async def close(self) -> None:
            return None

        async def publish(self, topic: str, key: object, value: bytes) -> object:
            return None

        async def subscribe(
            self,
            topic: str,
            *,
            on_message: Callable[[ProtocolLocalRuntimeMessage], Awaitable[None]],
            group_id: str,
        ) -> UnsubscribeCallback:
            return _unsub

    assert isinstance(_Bus(), ProtocolLocalRuntimeBus)

    class _PartialBus:
        async def start(self) -> None:
            return None

    assert not isinstance(_PartialBus(), ProtocolLocalRuntimeBus)


@pytest.mark.unit
def test_unsubscribe_callback_alias_is_callable_awaitable() -> None:
    async def _unsub() -> None:
        return None

    cb: UnsubscribeCallback = _unsub
    assert callable(cb)


@pytest.mark.unit
def test_protocols_reexported_from_runtime_package() -> None:
    from omnibase_spi.protocols.runtime import (
        ProtocolLocalRuntimeBus as Bus,
        ProtocolLocalRuntimeCallableTarget as Target,
        ProtocolLocalRuntimeDumpModel as Dump,
        ProtocolLocalRuntimeMessage as Msg,
        ProtocolLocalRuntimePayloadModel as Payload,
        UnsubscribeCallback as Unsub,
    )

    assert Bus is ProtocolLocalRuntimeBus
    assert Msg is ProtocolLocalRuntimeMessage
    assert Target is ProtocolLocalRuntimeCallableTarget
    assert Payload is ProtocolLocalRuntimePayloadModel
    assert Dump is ProtocolLocalRuntimeDumpModel
    assert Unsub is UnsubscribeCallback
