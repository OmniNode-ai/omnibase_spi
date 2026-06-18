# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Conformance tests for the OMN-13221 renderer + capability-negotiation protocols.

Validates that ``ProtocolRenderer`` and
``ProtocolRendererCapabilityNegotiator``:

- Are ``@runtime_checkable`` Protocol classes.
- Define their required methods.
- Cannot be instantiated directly.
- Accept structurally-compliant implementations via ``isinstance`` and reject
  partial / non-compliant ones.
- Compose the released ``ModelRendererCapabilityContract`` (omnibase_core
  v0.45.0) and the shipped ``EnumEmptyStateReason`` typed-block vocabulary.
"""

from __future__ import annotations

from typing import Any, Protocol

import pytest

from omnibase_core.enums.enum_accessibility_tier import EnumAccessibilityTier
from omnibase_core.enums.enum_empty_state_reason import EnumEmptyStateReason
from omnibase_core.enums.enum_renderer_interaction_model import (
    EnumRendererInteractionModel,
)
from omnibase_core.enums.enum_widget_type import EnumWidgetType
from omnibase_core.models.dashboard.model_action_contract import ModelActionContract
from omnibase_core.models.dashboard.model_component_contract import (
    ModelComponentContract,
)
from omnibase_core.models.dashboard.model_renderer_capability_contract import (
    ModelRendererCapabilityContract,
)
from omnibase_core.models.events.model_event_envelope import ModelEventEnvelope
from omnibase_core.models.primitives.model_semver import ModelSemVer
from omnibase_spi.protocols.dashboard import (
    ProtocolRenderer,
    ProtocolRendererCapabilityNegotiator,
)


def _capability() -> ModelRendererCapabilityContract:
    return ModelRendererCapabilityContract(
        renderer_id="ui.effect.web",
        platform="web",
        supported_component_kinds=(EnumWidgetType.CHART, EnumWidgetType.TABLE),
        interaction_model=EnumRendererInteractionModel.POINTER,
        accessibility_tier=EnumAccessibilityTier.AA,
        contract_version=ModelSemVer(major=1, minor=0, patch=0),
        supports_interaction=True,
        supports_streaming=True,
        supports_theming=False,
    )


def _component(
    kind: EnumWidgetType = EnumWidgetType.CHART,
) -> ModelComponentContract:
    return ModelComponentContract(
        component_id="component.demo",
        component_kind=kind,
        title="Demo",
        contract_version=ModelSemVer(major=1, minor=0, patch=0),
        data_bindings=(),
        actions=(),
        evidence_requirements=(),
        permission=None,
        supported_empty_state_reasons=(EnumEmptyStateReason.UPSTREAM_BLOCKED,),
    )


def _action() -> ModelActionContract:
    return ModelActionContract(
        action_id="action.demo",
        command_topic="onex.cmd.ui.demo-action.v1",
        label="Run",
        approval_gate=None,
        correlation_required=False,
    )


class CompliantRenderer:
    """A class that fully implements ``ProtocolRenderer``."""

    async def renderer_capability(self) -> ModelRendererCapabilityContract:
        return _capability()

    async def can_render(self, component: ModelComponentContract) -> bool:
        capability = await self.renderer_capability()
        return component.component_kind in capability.supported_component_kinds

    async def render(self, component: ModelComponentContract, data: Any) -> Any:
        return {"component_id": component.component_id, "data": data}

    async def emit_action(
        self, action: ModelActionContract, payload: Any
    ) -> ModelEventEnvelope[Any]:
        raise NotImplementedError


class PartialRenderer:
    """A class missing some ``ProtocolRenderer`` methods."""

    async def renderer_capability(self) -> ModelRendererCapabilityContract:
        return _capability()


class NonCompliantRenderer:
    """A class that implements none of ``ProtocolRenderer``."""


class CompliantNegotiator:
    """A class that fully implements ``ProtocolRendererCapabilityNegotiator``."""

    async def negotiate(
        self,
        component: ModelComponentContract,
        renderer_capability: ModelRendererCapabilityContract,
        *,
        is_fresh: bool,
    ) -> EnumEmptyStateReason | None:
        if not is_fresh:
            return EnumEmptyStateReason.UPSTREAM_BLOCKED
        if (
            component.component_kind
            not in renderer_capability.supported_component_kinds
        ):
            return EnumEmptyStateReason.UPSTREAM_BLOCKED
        return None


class PartialNegotiator:
    """A class missing the negotiate method."""


@pytest.mark.unit
class TestProtocolRendererStructure:
    def test_is_runtime_checkable(self) -> None:
        assert hasattr(ProtocolRenderer, "_is_runtime_protocol") or hasattr(
            ProtocolRenderer, "__runtime_protocol__"
        )

    def test_is_protocol(self) -> None:
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolRenderer.__mro__
        )

    def test_defines_required_methods(self) -> None:
        for method in ("renderer_capability", "can_render", "render", "emit_action"):
            assert method in dir(ProtocolRenderer)

    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            ProtocolRenderer()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolRendererCompliance:
    def test_compliant_passes_isinstance(self) -> None:
        assert isinstance(CompliantRenderer(), ProtocolRenderer)

    def test_partial_fails_isinstance(self) -> None:
        assert not isinstance(PartialRenderer(), ProtocolRenderer)

    def test_non_compliant_fails_isinstance(self) -> None:
        assert not isinstance(NonCompliantRenderer(), ProtocolRenderer)


@pytest.mark.unit
class TestProtocolRendererBehavior:
    async def test_capability_round_trips_core_model(self) -> None:
        renderer = CompliantRenderer()
        capability = await renderer.renderer_capability()
        assert isinstance(capability, ModelRendererCapabilityContract)
        assert capability.renderer_id == "ui.effect.web"

    async def test_can_render_uses_supported_kinds(self) -> None:
        renderer = CompliantRenderer()
        assert await renderer.can_render(_component(EnumWidgetType.CHART)) is True
        assert (
            await renderer.can_render(_component(EnumWidgetType.STATUS_GRID)) is False
        )

    async def test_render_returns_output(self) -> None:
        renderer = CompliantRenderer()
        out = await renderer.render(_component(), {"x": 1})
        assert out["component_id"] == "component.demo"


@pytest.mark.unit
class TestProtocolRendererCapabilityNegotiatorStructure:
    def test_is_runtime_checkable(self) -> None:
        assert hasattr(
            ProtocolRendererCapabilityNegotiator, "_is_runtime_protocol"
        ) or hasattr(ProtocolRendererCapabilityNegotiator, "__runtime_protocol__")

    def test_is_protocol(self) -> None:
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolRendererCapabilityNegotiator.__mro__
        )

    def test_defines_negotiate(self) -> None:
        assert "negotiate" in dir(ProtocolRendererCapabilityNegotiator)

    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            ProtocolRendererCapabilityNegotiator()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolRendererCapabilityNegotiatorCompliance:
    def test_compliant_passes_isinstance(self) -> None:
        assert isinstance(CompliantNegotiator(), ProtocolRendererCapabilityNegotiator)

    def test_partial_fails_isinstance(self) -> None:
        assert not isinstance(PartialNegotiator(), ProtocolRendererCapabilityNegotiator)


@pytest.mark.unit
class TestProtocolRendererCapabilityNegotiatorBehavior:
    async def test_fresh_supported_renders(self) -> None:
        negotiator = CompliantNegotiator()
        reason = await negotiator.negotiate(
            _component(EnumWidgetType.CHART), _capability(), is_fresh=True
        )
        assert reason is None

    async def test_stale_capability_blocks(self) -> None:
        negotiator = CompliantNegotiator()
        reason = await negotiator.negotiate(
            _component(EnumWidgetType.CHART), _capability(), is_fresh=False
        )
        assert reason is EnumEmptyStateReason.UPSTREAM_BLOCKED

    async def test_unsupported_kind_blocks(self) -> None:
        negotiator = CompliantNegotiator()
        reason = await negotiator.negotiate(
            _component(EnumWidgetType.STATUS_GRID), _capability(), is_fresh=True
        )
        assert reason is EnumEmptyStateReason.UPSTREAM_BLOCKED
