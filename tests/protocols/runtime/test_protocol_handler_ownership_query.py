# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Tests for ProtocolHandlerOwnershipQuery.

Validates the structural ``is_owned_here(node_name)`` protocol.
"""

from __future__ import annotations

import pytest

from omnibase_spi.protocols.runtime.protocol_handler_ownership_query import (
    ProtocolHandlerOwnershipQuery,
)


@pytest.mark.unit
def test_protocol_handler_ownership_query_accepts_compliant_impl() -> None:
    class _Impl:
        def is_owned_here(self, node_name: str) -> bool:
            return True

    assert isinstance(_Impl(), ProtocolHandlerOwnershipQuery)


@pytest.mark.unit
def test_protocol_handler_ownership_query_rejects_missing_method() -> None:
    class _Bad:
        pass

    assert not isinstance(_Bad(), ProtocolHandlerOwnershipQuery)


@pytest.mark.unit
def test_protocol_handler_ownership_query_reexported_from_runtime_package() -> None:
    from omnibase_spi.protocols.runtime import (
        ProtocolHandlerOwnershipQuery as ReExported,
    )

    assert ReExported is ProtocolHandlerOwnershipQuery
