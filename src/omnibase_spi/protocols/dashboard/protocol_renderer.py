# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for a renderer-as-effect-node (OMN-13221, Phase 1 of OMN-13129).

This module defines ``ProtocolRenderer`` — the boundary a renderer effect node
satisfies in the contract-driven UI platform. A renderer is an **effect node**:
it consumes a ``ModelComponentContract`` plus projection data and produces
renderable output, and — when a declared UI action fires — it emits a canonical
command envelope **onto the bus directly** (bus transport, no HTTP hop).

Architecture Context (plan
``docs/plans/2026-06-13-contract-driven-ui-platform-unified-plan.md`` §5b/§5c/§7,
invariant 2):

    1. Each renderer advertises its capability surface
       (``ModelRendererCapabilityContract``) on startup and on a heartbeat. This
       is the *producer* side of the Renderer Capability Registry projection
       (``node_renderer_capability_projection``, owned by omnimarket).
    2. The capability dispatcher (Phase 1) negotiates a component contract
       against a renderer's freshly-advertised capability before routing.
    3. The renderer renders a component contract against projection data.
    4. When a UI action contract fires, the renderer emits the action's declared
       ``onex.cmd.*`` command as a ``ModelEventEnvelope`` onto the bus. The
       generalized command loop replaces the bespoke
       ``browser → HTTP API → HTTP → bus`` delegation path.

Core Principle:
    A renderer is a pure, stateless transformer plus a thin command emitter. It
    holds no internal state between calls, fetches no data from external sources
    (data is passed in), and never constructs transport URLs or routes — the
    command topic is read from the ``ModelActionContract``. Concrete renderer
    effect nodes live in omnimarket / client packages, never in spi.

This module defines a pure ``typing.Protocol`` only: no implementation, no
daemon, no registry class. ``ProtocolWidgetRenderer`` (also in this domain) is an
UNRELATED pre-existing protocol that renders a ``ModelWidgetDefinition``; this
protocol renders the Phase-0 ``ModelComponentContract`` primitive and adds the
effect-node capability/emit surface.

Related tickets:
    - OMN-13221: renderer + capability-negotiation protocols.
    - OMN-13131: Phase 1 — close the runtime action loop (bus-native).
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from omnibase_core.models.dashboard.model_action_contract import ModelActionContract
from omnibase_core.models.dashboard.model_component_contract import (
    ModelComponentContract,
)
from omnibase_core.models.dashboard.model_renderer_capability_contract import (
    ModelRendererCapabilityContract,
)
from omnibase_core.models.events.model_event_envelope import ModelEventEnvelope

__all__ = ["ProtocolRenderer"]


@runtime_checkable
class ProtocolRenderer(Protocol):
    """Interface for a renderer effect node in the contract-driven UI platform.

    A renderer transforms a ``ModelComponentContract`` plus projection data into
    renderable output, advertises the capability surface it guarantees, and emits
    a renderer's declared command actions onto the bus.

    Renderers MUST:
        - Be stateless and produce consistent output for the same inputs.
        - Advertise a ``ModelRendererCapabilityContract`` via
          ``renderer_capability()`` for the capability projection producer side.
        - Read the command topic for an emitted action from its
          ``ModelActionContract`` — never hardcode or construct a topic.

    Renderers MUST NOT:
        - Maintain internal state between calls.
        - Fetch data from external sources (data is passed in).
        - Construct transport URLs/routes or emit over HTTP (bus transport only).
        - Mutate the input component, action, or data.
    """

    async def renderer_capability(self) -> ModelRendererCapabilityContract:
        """Return the capability surface this renderer advertises.

        This is the *producer* side of the Renderer Capability Registry
        projection: the renderer declares the component kinds it supports, its
        interaction model, accessibility tier, granular ``supports_*`` flags, and
        capability contract version. The omnimarket
        ``node_renderer_capability_projection`` reducer consumes this declaration
        on startup and on a heartbeat to materialize the projection.

        Returns:
            The renderer's advertised ``ModelRendererCapabilityContract``.
        """
        ...

    async def can_render(self, component: ModelComponentContract) -> bool:
        """Check whether this renderer can render the given component contract.

        Consistent with ``renderer_capability()``: returns ``True`` only when the
        component's ``component_kind`` is in the renderer's advertised
        ``supported_component_kinds``. Capability negotiation across renderers is
        the dispatcher's concern (``ProtocolRendererCapabilityNegotiator``); this
        is the renderer-local self-check.

        Args:
            component: The component contract to test for renderability.

        Returns:
            ``True`` if this renderer can render the component, else ``False``.
        """
        ...

    async def render(
        self,
        component: ModelComponentContract,
        data: Any,
    ) -> Any:
        """Render a component contract against its projection data.

        Pure transformation: same inputs produce the same output with no side
        effects. The output format depends on the concrete renderer (HTML string,
        JSON dict for a frontend, or framework-specific component data). The
        renderer must handle empty or absent data by surfacing the contract's
        declared empty-state reasons rather than rendering blind.

        Args:
            component: The component contract describing what to render
                (kind, bindings, actions, evidence requirements, permission).
            data: The projection data to render. Structure depends on the
                component kind; may be ``None`` when no data is available.

        Returns:
            Rendered output for the component; type depends on the renderer.

        Raises:
            SPIError: If rendering fails due to an incompatible component or data
                shape. Implementations may raise a rendering-specific subclass.
        """
        ...

    async def emit_action(
        self,
        action: ModelActionContract,
        payload: Any,
    ) -> ModelEventEnvelope[Any]:
        """Emit a declared UI action as a command envelope onto the bus.

        When a user triggers a declared action, the renderer effect node builds
        the action's canonical ``onex.cmd.*`` command (the topic is read from
        ``action.command_topic`` — never constructed) and publishes it onto the
        bus directly over bus transport. This generalizes the previously bespoke
        ``browser → HTTP API → HTTP → bus`` delegation path to all actions and
        removes both HTTP hops from the action path.

        The returned envelope is the published command, enabling correlation
        tracking when ``action.correlation_required`` is set and downstream
        projection round-trips.

        Args:
            action: The action contract declaring the command topic and its
                approval/commit gate.
            payload: The user-supplied command payload for the action.

        Returns:
            The published command as a ``ModelEventEnvelope``.

        Raises:
            SPIError: If the action cannot be emitted (e.g. an unsatisfied
                approval gate). Implementations may raise a subclass.
        """
        ...
