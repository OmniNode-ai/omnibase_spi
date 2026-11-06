# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ProtocolOverlayStore is structural: a full store passes, a partial one does not."""

from collections.abc import Mapping

import pytest

from omnibase_core.types import JsonType
from omnibase_spi.protocols.storage import ProtocolOverlayStore


class _FullStore:
    async def write_version(self, record: Mapping[str, JsonType]) -> bool:
        return True

    async def read_current(self, overlay_id: str) -> Mapping[str, JsonType] | None:
        return None


class _ReadOnlyStore:
    async def read_current(self, overlay_id: str) -> Mapping[str, JsonType] | None:
        return None


@pytest.mark.unit
def test_a_full_store_is_the_protocol() -> None:
    assert isinstance(_FullStore(), ProtocolOverlayStore)


@pytest.mark.unit
def test_a_store_that_cannot_write_is_not_the_protocol() -> None:
    assert not isinstance(_ReadOnlyStore(), ProtocolOverlayStore)
