# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for SkillRoutingError — internal issue."""

from __future__ import annotations

import pytest

from omnibase_spi.exceptions_skill_routing import SkillRoutingError


@pytest.mark.unit
class TestSkillRoutingError:
    def test_basic_raise(self) -> None:
        with pytest.raises(SkillRoutingError):
            raise SkillRoutingError("node unavailable", skill_name="my_skill")

    def test_inherits_spi_error(self) -> None:
        from omnibase_spi.exceptions import SPIError

        err = SkillRoutingError("x", skill_name="s", node_target="n")
        assert isinstance(err, SPIError)

    def test_structured_fields_on_permanent(self) -> None:
        err = SkillRoutingError(
            "route failed",
            skill_name="summarize",
            node_target="node-01",
            failure_reason="node_unavailable",
            error_type="permanent",
            attempted_routes=["route-a", "route-b"],
            last_error="connection refused",
        )
        assert err.skill_name == "summarize"
        assert err.node_target == "node-01"
        assert err.failure_reason == "node_unavailable"
        assert err.error_type == "permanent"
        assert err.attempted_routes == ["route-a", "route-b"]
        assert err.last_error == "connection refused"
        assert not err.is_transient

    def test_transient_flag(self) -> None:
        err = SkillRoutingError("timeout", skill_name="s", error_type="transient")
        assert err.is_transient

    def test_default_empty_routes(self) -> None:
        err = SkillRoutingError("x", skill_name="s")
        assert err.attempted_routes == []

    def test_context_contains_structured_fields(self) -> None:
        err = SkillRoutingError(
            "x",
            skill_name="s",
            node_target="n",
            failure_reason="unavailable",
            error_type="permanent",
        )
        assert err.context["skill_name"] == "s"
        assert err.context["node_target"] == "n"
        assert err.context["failure_reason"] == "unavailable"
        assert err.context["error_type"] == "permanent"

    def test_kafka_payload_shape(self) -> None:
        err = SkillRoutingError(
            "x",
            skill_name="summarize",
            node_target="node-01",
            failure_reason="node_unavailable",
            error_type="permanent",
        )
        payload = err.kafka_payload()
        assert payload["event_type"] == "onex.evt.omniclaude.skill-routing-failed.v1"
        assert payload["skill_name"] == "summarize"
        assert payload["node_target"] == "node-01"
        assert payload["failure_reason"] == "node_unavailable"
        assert payload["error_type"] == "permanent"

    def test_lazy_import_from_package_root(self) -> None:
        from omnibase_spi import SkillRoutingError as SRE

        assert SRE is SkillRoutingError

    def test_no_prose_emitted_on_raise(self) -> None:
        """Raising SkillRoutingError must not produce unstructured prose output."""
        err = SkillRoutingError("node unavailable", skill_name="s")
        assert str(err) == "node unavailable"
