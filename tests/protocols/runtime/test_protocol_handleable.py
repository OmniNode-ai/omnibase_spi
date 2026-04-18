# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Tests for ProtocolHandleable.

Validates the structural ``handle()`` protocol used by the auto-wiring
engine to type-check handler instances before dispatcher registration.
"""

from __future__ import annotations

import pytest

from omnibase_spi.protocols.runtime.protocol_handleable import ProtocolHandleable


@pytest.mark.unit
def test_protocol_handleable_accepts_object_with_async_handle() -> None:
    class _Impl:
        async def handle(self, envelope: object) -> object | None:
            return None

    assert isinstance(_Impl(), ProtocolHandleable)


@pytest.mark.unit
def test_protocol_handleable_rejects_object_without_handle() -> None:
    class _Bad:
        pass

    assert not isinstance(_Bad(), ProtocolHandleable)


@pytest.mark.unit
def test_protocol_handleable_reexported_from_runtime_package() -> None:
    from omnibase_spi.protocols.runtime import ProtocolHandleable as ReExported

    assert ReExported is ProtocolHandleable
