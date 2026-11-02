# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""OMN-22000: ProtocolClock resolves from the core protocol domain and checks structurally."""

from datetime import UTC, datetime

import pytest

from omnibase_spi.protocols import ProtocolClock as ProtocolClockTop
from omnibase_spi.protocols.core import ProtocolClock as ProtocolClockCore
from omnibase_spi.protocols.core.protocol_clock import ProtocolClock


class _FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 11, 2, 11, 0, tzinfo=UTC)


class _NoClock:
    def utcnow(self) -> datetime:
        return datetime(2026, 11, 2, 11, 0, tzinfo=UTC)


@pytest.mark.unit
def test_every_import_path_names_one_protocol() -> None:
    assert ProtocolClockCore is ProtocolClock
    assert ProtocolClockTop is ProtocolClock


@pytest.mark.unit
def test_an_object_with_now_is_a_clock() -> None:
    assert isinstance(_FixedClock(), ProtocolClock)
    assert _FixedClock().now() == datetime(2026, 11, 2, 11, 0, tzinfo=UTC)


@pytest.mark.unit
def test_an_object_without_now_is_not_a_clock() -> None:
    assert not isinstance(_NoClock(), ProtocolClock)
