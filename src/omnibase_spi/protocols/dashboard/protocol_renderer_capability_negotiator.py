# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Capability-negotiation protocol (OMN-13221, Phase 1 of OMN-13129).

This module defines ``ProtocolRendererCapabilityNegotiator`` — the boundary the
Phase-1 capability dispatcher satisfies when deciding whether a
``ModelComponentContract`` may be routed to a renderer given that renderer's
freshly-advertised ``ModelRendererCapabilityContract``.

Architecture Context (plan
``docs/plans/2026-06-13-contract-driven-ui-platform-unified-plan.md`` §7
"Renderer Capability Registry — ownership spec"):

    - Each renderer publishes its ``ModelRendererCapabilityContract`` on startup
      and on a heartbeat; the omnimarket ``node_renderer_capability_projection``
      reducer materializes the projection with a ``last_heartbeat`` freshness
      column.
    - Past the heartbeat TTL a renderer row is ``degraded`` (not fresh).
    - **Client negotiation when stale/absent:** the projection service does NOT
      route a UI component contract to a renderer whose capability row does not
      currently and freshly advertise the required component kind. Instead it
      surfaces a *typed* ``upstream-blocked`` empty-state reason rather than
      rendering blind.

Core Principle:
    Negotiation is a pure, stateless decision: ``(component, capability,
    freshness) → renderable | typed block reason``. It composes the released
    ``ModelRendererCapabilityContract`` and the shipped ``EnumEmptyStateReason``
    vocabulary; it introduces no new model. A ``None`` result means the component
    may be routed to the renderer; a non-``None`` ``EnumEmptyStateReason`` is the
    typed reason the client must surface instead of rendering.

This module defines a pure ``typing.Protocol`` only: no implementation, no
daemon, no registry class. ``ProtocolCapabilityRegistry`` (in the ``registry``
domain) is an UNRELATED pre-existing protocol and is NOT this surface.

Related tickets:
    - OMN-13221: renderer + capability-negotiation protocols.
    - OMN-13131: Phase 1 — close the runtime action loop (bus-native).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from omnibase_core.enums.enum_empty_state_reason import EnumEmptyStateReason
from omnibase_core.models.dashboard.model_component_contract import (
    ModelComponentContract,
)
from omnibase_core.models.dashboard.model_renderer_capability_contract import (
    ModelRendererCapabilityContract,
)

__all__ = ["ProtocolRendererCapabilityNegotiator"]


@runtime_checkable
class ProtocolRendererCapabilityNegotiator(Protocol):
    """Interface for negotiating a component contract against a renderer.

    The negotiator decides whether a ``ModelComponentContract`` may be routed to
    a renderer given that renderer's advertised
    ``ModelRendererCapabilityContract`` and its current projection freshness.

    Negotiators MUST:
        - Be stateless and produce a consistent decision for the same inputs.
        - Return ``None`` only when the renderer freshly advertises support for
          the component's required capability surface.
        - Return a typed ``EnumEmptyStateReason`` (``upstream-blocked``) when the
          renderer's capability is stale/absent or does not cover the component
          kind — never let the client render blind.

    Negotiators MUST NOT:
        - Maintain internal state between calls.
        - Perform I/O or query a registry directly (freshness is passed in).
        - Construct or mutate the component or capability contracts.
    """

    async def negotiate(
        self,
        component: ModelComponentContract,
        renderer_capability: ModelRendererCapabilityContract,
        *,
        is_fresh: bool,
    ) -> EnumEmptyStateReason | None:
        """Negotiate routing a component contract to a renderer.

        Decides whether ``component`` may be routed to the renderer described by
        ``renderer_capability`` given that capability row's freshness. The
        decision composes the renderer's advertised
        ``supported_component_kinds``, interaction model, accessibility tier, and
        granular ``supports_*`` flags against the component's requirements.

        Args:
            component: The UI component contract to route.
            renderer_capability: The renderer's advertised capability surface as
                materialized by the Renderer Capability Registry projection.
            is_fresh: Whether the capability row is within its heartbeat TTL.
                A stale (``False``) row must block.

        Returns:
            ``None`` when the component may be routed to the renderer; otherwise
            the typed ``EnumEmptyStateReason`` (``upstream-blocked``) the client
            must surface instead of rendering.
        """
        ...
