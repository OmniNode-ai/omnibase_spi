# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""SkillRoutingError — structured exception for shim routing failures."""

from __future__ import annotations

from typing import Any

from omnibase_spi.exceptions import SPIError


class SkillRoutingError(SPIError):
    """Raised when a skill shim cannot route to any available node.

    Emits onex.evt.omniclaude.skill-routing-failed.v1 on every failure.
    Permanent vs transient failures are distinguished via ``is_transient``.

    Args:
        message: Human-readable description of the routing failure.
        skill_name: Canonical name of the skill that failed to route.
        node_target: Node or target identifier that was attempted.
        failure_reason: Short structured reason code (e.g. "node_unavailable").
        error_type: "transient" or "permanent".
        attempted_routes: Ordered list of route identifiers that were tried.
        last_error: Underlying exception or error string, if available.
        context: Additional structured debugging fields.
    """

    def __init__(
        self,
        message: str = "",
        *,
        skill_name: str = "",
        node_target: str = "",
        failure_reason: str = "",
        error_type: str = "permanent",
        attempted_routes: list[str] | None = None,
        last_error: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        routes = list(attempted_routes or [])
        merged: dict[str, Any] = dict(context or {})
        merged.update(
            {
                "skill_name": skill_name,
                "node_target": node_target,
                "failure_reason": failure_reason,
                "error_type": error_type,
                "attempted_routes": routes,
                "last_error": last_error,
            }
        )
        super().__init__(message, context=merged)
        self.skill_name = skill_name
        self.node_target = node_target
        self.failure_reason = failure_reason
        self.error_type = error_type
        self.attempted_routes: list[str] = routes
        self.last_error = last_error

    @property
    def is_transient(self) -> bool:
        return self.error_type == "transient"

    def kafka_payload(self) -> dict[str, Any]:
        """Return the canonical Kafka event payload for skill-routing-failed.v1."""
        return {
            "event_type": "onex.evt.omniclaude.skill-routing-failed.v1",
            "skill_name": self.skill_name,
            "node_target": self.node_target,
            "failure_reason": self.failure_reason,
            "error_type": self.error_type,
        }
