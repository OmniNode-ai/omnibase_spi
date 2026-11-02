# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Wire-format contracts for ProtocolLaneHostPool: one request, one pool snapshot.

This module MUST NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from pydantic import BaseModel, ConfigDict, Field

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class ModelLaneHostPoolRequest(BaseModel):
    """Ask for the pool as seen for one engine.

    Attributes:
        engine: The engine the lane will run.
        pinned_host: A host the caller pins the lane to, if any.
        lane: The lane asking, if known.
    """

    model_config = _FROZEN

    engine: str = Field(..., description="Engine the lane will run.")
    pinned_host: str | None = Field(default=None, description="Pinned host, if any.")
    lane: str | None = Field(default=None, description="Lane asking, if known.")


class ModelLaneHostPoolReading(BaseModel):
    """One host's capacity and readiness reading.

    Attributes:
        name: Host name.
        target: How to reach the host; None for none.
        local: True when the host is the caller's own machine.
        engines: Engines the host can run.
        lane_admission_refusal: Why the host refuses a new lane, if it does.
        codex_refusal: Why the host refuses the codex engine, if it does.
        lane_slots: Lane slots in use.
        lane_cap: Lane slots the host allows.
        placed: Lanes already placed on the host this round.
        rank_free: Free-capacity rank; None when unreadable.
        mem_avail_gb: Available memory in GB.
        dispatch_venv_hash: Hash of the host's dispatch venv, if known.
        contributor: True when the host contributes capacity to the pool.
        bus_lane: The bus lane the host listens on, if any.
        lane_ready: True when the host is ready to take a lane.
        lane_not_ready_reason: Why the host is not ready, if it is not.
    """

    model_config = _FROZEN

    name: str = Field(..., description="Host name.")
    target: str | None = Field(default=None, description="Address or ssh target.")
    local: bool = Field(default=False, description="True for the caller's own machine.")
    engines: tuple[str, ...] = Field(default=(), description="Engines the host runs.")
    lane_admission_refusal: str | None = Field(
        default=None, description="Why the host refuses a new lane."
    )
    codex_refusal: str | None = Field(
        default=None, description="Why the host refuses the codex engine."
    )
    lane_slots: int = Field(default=0, description="Lane slots in use.")
    lane_cap: int = Field(default=0, description="Lane slots the host allows.")
    placed: int = Field(default=0, ge=0, description="Lanes placed this round.")
    rank_free: float | None = Field(
        default=0.0, description="Free-capacity rank; None when unreadable."
    )
    mem_avail_gb: float = Field(default=0.0, description="Available memory in GB.")
    dispatch_venv_hash: str | None = Field(
        default=None, description="Hash of the dispatch venv."
    )
    contributor: bool = Field(default=False, description="Contributes capacity.")
    bus_lane: str | None = Field(default=None, description="Bus lane of the host.")
    lane_ready: bool = Field(default=False, description="Ready to take a lane.")
    lane_not_ready_reason: str | None = Field(
        default=None, description="Why the host is not ready."
    )


class ModelLaneHostPoolSnapshot(BaseModel):
    """The pool at one moment.

    Attributes:
        readings: One reading per host.
        limited_hosts: Hosts that hit a usage limit.
        codex_limited_hosts: Hosts whose codex engine hit a usage limit.
        auth_expired_hosts: Hosts whose engine login has expired.
        launching_venv_hash: Hash of the launching machine's dispatch venv.
    """

    model_config = _FROZEN

    readings: tuple[ModelLaneHostPoolReading, ...] = Field(
        default=(), description="One reading per host."
    )
    limited_hosts: tuple[str, ...] = Field(
        default=(), description="Hosts that hit a usage limit."
    )
    codex_limited_hosts: tuple[str, ...] = Field(
        default=(), description="Hosts whose codex engine hit a usage limit."
    )
    auth_expired_hosts: tuple[str, ...] = Field(
        default=(), description="Hosts whose engine login has expired."
    )
    launching_venv_hash: str | None = Field(
        default=None, description="Dispatch venv hash of the launching machine."
    )


__all__ = [
    "ModelLaneHostPoolReading",
    "ModelLaneHostPoolRequest",
    "ModelLaneHostPoolSnapshot",
]
