# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Checks every ProtocolLaneHostPool adapter must pass (OMN-22198).

A real adapter is wrapped in a harness that arranges which hosts the pool holds
and which limits it reports.
"""

from collections.abc import Callable
from typing import Protocol

from omnibase_spi.contracts.services import (
    ModelLaneHostPoolReading,
    ModelLaneHostPoolRequest,
    ModelLaneHostPoolSnapshot,
)
from omnibase_spi.protocols.lane import ProtocolLaneHostPool


class LanePoolHarness(Protocol):
    pool: ProtocolLaneHostPool

    def arrange(self, snapshot: ModelLaneHostPoolSnapshot) -> None: ...


def check_is_protocol_instance(h: LanePoolHarness) -> None:
    assert isinstance(h.pool, ProtocolLaneHostPool)


def check_an_empty_pool_is_an_empty_snapshot(h: LanePoolHarness) -> None:
    h.arrange(ModelLaneHostPoolSnapshot())
    snapshot = h.pool.read_pool(ModelLaneHostPoolRequest(engine="claude"))
    assert snapshot.readings == () and snapshot.limited_hosts == ()


def check_every_host_reading_and_every_limit_comes_back(h: LanePoolHarness) -> None:
    h.arrange(
        ModelLaneHostPoolSnapshot(
            readings=(
                ModelLaneHostPoolReading(
                    name="host-a", engines=("claude", "codex"), lane_ready=True
                ),
                ModelLaneHostPoolReading(
                    name="host-b",
                    local=True,
                    lane_ready=False,
                    lane_not_ready_reason="venv stale",
                ),
            ),
            limited_hosts=("host-b",),
            codex_limited_hosts=("host-a",),
            auth_expired_hosts=("host-c",),
            launching_venv_hash="abc123",
        )
    )
    snapshot = h.pool.read_pool(
        ModelLaneHostPoolRequest(engine="codex", pinned_host="host-a", lane="lane-1")
    )
    assert tuple(r.name for r in snapshot.readings) == ("host-a", "host-b")
    assert snapshot.readings[0].lane_ready is True
    assert snapshot.readings[1].lane_not_ready_reason == "venv stale"
    assert snapshot.limited_hosts == ("host-b",)
    assert snapshot.codex_limited_hosts == ("host-a",)
    assert snapshot.auth_expired_hosts == ("host-c",)
    assert snapshot.launching_venv_hash == "abc123"


CHECKS: tuple[Callable[[LanePoolHarness], None], ...] = (
    check_is_protocol_instance,
    check_an_empty_pool_is_an_empty_snapshot,
    check_every_host_reading_and_every_limit_comes_back,
)
