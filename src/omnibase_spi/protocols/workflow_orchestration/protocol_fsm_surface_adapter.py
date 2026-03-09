"""Protocol interface for FSM surface adapters in ONEX systems."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.contracts.subcontracts.model_fsm_state_definition import (
        ModelFSMStateDefinition,
    )
    from omnibase_core.models.fsm.model_fsm_state_snapshot import ModelFSMStateSnapshot


@runtime_checkable
class ProtocolFSMSurfaceAdapter(Protocol):
    """Protocol for rendering an FSM state to a target presentation surface.

    Surface adapters are responsible for translating FSM state snapshots into
    surface-specific payloads suitable for delivery channels such as UI rendering,
    voice assistants, push notifications, chat interfaces, and CLI summaries.

    The surface parameter uses lowercase snake_case stable identifiers
    (e.g., 'web_ui', 'voice', 'push_notification', 'chat', 'cli').
    Using str rather than an enum allows new surfaces to be added without
    requiring schema changes in the SPI layer.

    Core model imports are TYPE_CHECKING-only to preserve the SPI purity
    boundary — no Core runtime dependency at import time.
    """

    async def render(
        self,
        state: ModelFSMStateDefinition,
        snapshot: ModelFSMStateSnapshot,
        surface: str,
    ) -> dict[str, object]:
        """Render an FSM state to a surface-specific payload.

        Args:
            state: The FSM state definition containing metadata and semantic_intent.
            snapshot: The current FSM state snapshot with runtime values.
            surface: Target surface identifier (lowercase snake_case, e.g., 'web_ui').

        Returns:
            A surface-specific dict payload ready for delivery to the target surface.
        """
        ...

    async def supported_surfaces(self) -> list[str]:
        """Return the surface identifiers this adapter supports.

        Returns:
            List of surface identifier strings this adapter can render for.
        """
        ...
