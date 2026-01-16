"""Protocol for dashboard widget rendering.

This module defines the contract for widget renderers that transform widget
definitions and data into renderable output for dashboard visualization.

Architecture Context:
    In the ONEX dashboard architecture, widget renderers serve as the
    transformation layer between widget definitions and rendered output:

    1. Dashboard loads widget definitions from configuration
    2. Data is fetched for each widget from its data source
    3. Widget renderer transforms definition + data into renderable output
    4. Output is consumed by the dashboard frontend for display
    5. Renderers can output HTML, JSON, or framework-specific components

Core Principle:
    Widget renderers are pure transformers - they take a widget definition
    and data, and produce rendered output. They should:
    - Be stateless and side-effect free
    - Support multiple widget types via get_supported_types()
    - Handle missing or malformed data gracefully
    - Return consistent output formats per widget type

Widget Type Support:
    Renderers declare which widget types they support. A renderer may be:
    - Specialized: Handles one specific widget type (e.g., chart renderer)
    - General: Handles multiple widget types (e.g., HTML renderer)
    - Composite: Delegates to specialized renderers based on widget type

Output Formats:
    Rendered output varies by renderer implementation:
    - HTML renderers: Return HTML string or fragment
    - JSON renderers: Return serializable dict for frontend frameworks
    - Component renderers: Return framework-specific component data

Sequence Diagram:
    ```
    Dashboard       Renderer         WidgetDef         Data
       |               |                 |               |
       |-- render ---->|                 |               |
       |               |-- read type --->|               |
       |               |-- read config ->|               |
       |               |-- transform ------------------->|
       |               |<-- output ------|               |
       |<-- result ----|                 |               |
       |               |                 |               |
    ```

Related tickets:
    - OMN-1285: Create dashboard protocols for omnibase_spi
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.enums import EnumWidgetType
    from omnibase_core.models.dashboard import ModelWidgetDefinition


@runtime_checkable
class ProtocolWidgetRenderer(Protocol):
    """Interface for dashboard widget rendering.

    Widget renderers transform ModelWidgetDefinition and associated data
    into renderable output for dashboard visualization. They are pure
    transformers with no side effects beyond producing output.

    Renderers MUST:
        - Be stateless and produce consistent output for same inputs
        - Declare supported widget types via get_supported_types()
        - Handle missing or malformed data gracefully with defaults
        - Return output in a consistent format per widget type

    Renderers SHOULD:
        - Validate widget type before rendering
        - Use can_render() to check compatibility
        - Provide meaningful error output for unsupported types
        - Support theming and styling configuration

    Renderers MUST NOT:
        - Maintain internal state between render calls
        - Fetch data from external sources (data is passed in)
        - Modify the input widget definition or data
        - Have side effects beyond producing output

    Example Usage:
        ```python
        from omnibase_core.enums import EnumWidgetType
        from omnibase_core.models.dashboard import ModelWidgetDefinition


        class HtmlWidgetRenderer:
            async def get_supported_types(self) -> Sequence[EnumWidgetType]:
                return [
                    EnumWidgetType.CHART,
                    EnumWidgetType.TABLE,
                    EnumWidgetType.METRIC,
                ]

            async def can_render(self, widget_type: EnumWidgetType) -> bool:
                supported = await self.get_supported_types()
                return widget_type in supported

            async def render_widget(
                self,
                widget: ModelWidgetDefinition,
                data: Any,
            ) -> str:
                if not await self.can_render(widget.widget_type):
                    return f"<div>Unsupported widget: {widget.widget_type}</div>"

                if widget.widget_type == EnumWidgetType.CHART:
                    return self._render_chart(widget, data)
                elif widget.widget_type == EnumWidgetType.TABLE:
                    return self._render_table(widget, data)
                # ...


        # Usage in dashboard
        renderer: ProtocolWidgetRenderer = HtmlWidgetRenderer()

        for widget in dashboard.widgets:
            if await renderer.can_render(widget.widget_type):
                html = await renderer.render_widget(widget, widget_data[widget.id])
                output.append(html)
        ```

    Implementation Notes:
        - Concrete implementations live in omnibase_infra
        - Renderers may be composed for multi-format output
        - Output format depends on frontend technology choice
    """

    async def get_supported_types(self) -> Sequence[EnumWidgetType]:
        """Get the widget types this renderer supports.

        Returns the sequence of widget types that this renderer can
        handle. Used for:
            - Routing widgets to appropriate renderers
            - Validation before rendering
            - Documentation and introspection

        A renderer may support multiple widget types if it has
        generalized rendering logic, or a single type if specialized.

        Returns:
            Sequence of EnumWidgetType values this renderer supports.
            Should return an empty sequence if no types are supported.

        Example:
            ```python
            async def get_supported_types(self) -> Sequence[EnumWidgetType]:
                return [
                    EnumWidgetType.CHART,
                    EnumWidgetType.TABLE,
                    EnumWidgetType.METRIC,
                    EnumWidgetType.TEXT,
                ]
            ```
        """
        ...

    async def can_render(self, widget_type: EnumWidgetType) -> bool:
        """Check if this renderer can handle the given widget type.

        Convenience method to check widget type compatibility before
        calling render_widget(). This allows callers to:
            - Route to appropriate renderers
            - Provide fallback handling for unsupported types
            - Validate configurations early

        This method should be consistent with get_supported_types(),
        returning True only for types in that sequence.

        Args:
            widget_type: The widget type to check for support.

        Returns:
            True if this renderer can render the widget type,
            False otherwise.

        Example:
            ```python
            async def can_render(self, widget_type: EnumWidgetType) -> bool:
                supported = await self.get_supported_types()
                return widget_type in supported
            ```
        """
        ...

    async def render_widget(
        self,
        widget: ModelWidgetDefinition,
        data: Any,
    ) -> Any:
        """Render a widget with its associated data.

        Transforms a widget definition and data into renderable output.
        The output format depends on the renderer implementation:
            - HTML renderers: Return HTML string
            - JSON renderers: Return dict for frontend serialization
            - Component renderers: Return framework-specific data

        This method MUST be pure - same inputs produce same outputs
        with no side effects. The renderer should handle edge cases:
            - Empty or None data: Render with appropriate defaults
            - Malformed data: Render error state or fallback
            - Unsupported widget type: Return error indicator

        Args:
            widget: The widget definition containing:
                - widget_type: The type of widget to render
                - title: Display title for the widget
                - config: Widget-specific configuration
                - layout: Position and size information
            data: The data to render in the widget. Structure depends
                on widget type (e.g., list for tables, dict for charts).
                May be None if no data is available.

        Returns:
            Rendered output for the widget. Type depends on renderer:
                - str: HTML string for HTML renderers
                - dict: JSON-serializable dict for JSON renderers
                - Any: Framework-specific data for component renderers

        Raises:
            SPIError: If rendering fails due to invalid widget definition
                or incompatible data format. Implementations may raise
                a rendering-specific subclass.

        Example:
            ```python
            async def render_widget(
                self,
                widget: ModelWidgetDefinition,
                data: Any,
            ) -> str:
                if widget.widget_type == EnumWidgetType.METRIC:
                    value = data.get("value", 0) if data else 0
                    label = widget.config.get("label", widget.title)
                    return f'''
                        <div class="metric-widget">
                            <span class="value">{value}</span>
                            <span class="label">{label}</span>
                        </div>
                    '''

                if widget.widget_type == EnumWidgetType.TABLE:
                    rows = data or []
                    columns = widget.config.get("columns", [])
                    return self._render_table_html(columns, rows)

                return f"<div>Unknown widget type: {widget.widget_type}</div>"
            ```
        """
        ...
