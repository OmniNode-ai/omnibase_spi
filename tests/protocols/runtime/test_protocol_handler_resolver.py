# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Tests for ProtocolHandlerResolver.

Validates the structural ``resolve(context)`` protocol. The spi layer
declares ``context: object`` — concrete implementations in
``omnibase_core`` narrow it to ``ModelHandlerResolverContext``.
"""

from __future__ import annotations

import pytest

from omnibase_spi.protocols.runtime.protocol_handler_resolver import (
    ProtocolHandlerResolver,
)


@pytest.mark.unit
def test_protocol_handler_resolver_is_runtime_checkable() -> None:
    class _Impl:
        def resolve(self, context: object) -> object:
            return context

    assert isinstance(_Impl(), ProtocolHandlerResolver)


@pytest.mark.unit
def test_protocol_handler_resolver_rejects_missing_resolve() -> None:
    class _Bad:
        pass

    assert not isinstance(_Bad(), ProtocolHandlerResolver)


@pytest.mark.unit
def test_protocol_handler_resolver_reexported_from_runtime_package() -> None:
    from omnibase_spi.protocols.runtime import ProtocolHandlerResolver as ReExported

    assert ReExported is ProtocolHandlerResolver
