"""Dashboard domain protocols for ONEX.

This domain contains protocols for dashboard services that provide real-time
visualization, monitoring, and UI integration capabilities for the ONEX
platform. These protocols define contracts for dashboard lifecycle management,
registry queries, widget rendering, and event-driven updates.

Architecture Overview:
    The dashboard domain follows a separation of concerns pattern:

    1. Service Layer (ProtocolDashboardService):
       - Dashboard configuration and lifecycle management
       - Registration/unregistration with platform registries
       - Identity and state tracking

    2. Query Layer (ProtocolRegistryQueryService):
       - Read-only access to node registry information
       - View model transformation for UI display
       - CQRS-style separation from write operations

    3. Rendering Layer (ProtocolWidgetRenderer):
       - Pure transformation of widget definitions to output
       - Multi-format support (HTML, JSON, components)
       - Stateless, side-effect-free rendering

    4. Event Layer (ProtocolDashboardEventSubscriber):
       - Real-time event subscription for live updates
       - Topic-based event routing
       - Callback-driven event delivery

Data Flow:
    ```
    Event Bus     Dashboard Service     Query Service     Widget Renderer
        |               |                    |                   |
        |-- events ---->|                    |                   |
        |               |-- get config ----->|                   |
        |               |-- query nodes ---->|                   |
        |               |                    |-- node views ---->|
        |               |                    |                   |-- render -->
        |               |<------------------ rendered output ----|
    ```

Protocols in this Domain:
    - ProtocolDashboardService: Dashboard lifecycle management including
      configuration retrieval, registration, and state tracking.

    - ProtocolDashboardEventSubscriber: Real-time event subscription for
      live dashboard updates without polling.

    - ProtocolRegistryQueryService: Read-only registry queries providing
      view models for UI components (nodes, capabilities, contracts).

    - ProtocolWidgetRenderer: Widget rendering that transforms definitions
      and data into displayable output (HTML, JSON, or framework-specific).

Usage Pattern:
    ```python
    from omnibase_spi.protocols.dashboard import (
        ProtocolDashboardService,
        ProtocolDashboardEventSubscriber,
        ProtocolRegistryQueryService,
        ProtocolWidgetRenderer,
    )

    # Type-check implementations
    def setup_dashboard(
        service: ProtocolDashboardService,
        query: ProtocolRegistryQueryService,
        renderer: ProtocolWidgetRenderer,
        subscriber: ProtocolDashboardEventSubscriber,
    ) -> None:
        # Configure and start dashboard
        ...
    ```

Related tickets:
    - OMN-1285: Dashboard Protocols (omnibase_spi)
"""

from .protocol_dashboard_event_subscriber import ProtocolDashboardEventSubscriber
from .protocol_dashboard_service import ProtocolDashboardService
from .protocol_registry_query_service import ProtocolRegistryQueryService
from .protocol_widget_renderer import ProtocolWidgetRenderer

__all__ = [
    "ProtocolDashboardEventSubscriber",
    "ProtocolDashboardService",
    "ProtocolRegistryQueryService",
    "ProtocolWidgetRenderer",
]
