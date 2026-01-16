"""Protocol for output formatting in ONEX workflows.

This module defines the interface for output formatters that transform data
according to specified styles and formats for consistent presentation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_advanced_types import (
        ProtocolOutputData,
        ProtocolOutputFormat,
    )


@runtime_checkable
class ProtocolOutputFormatter(Protocol):
    """
    Protocol for output formatting in ONEX workflows with style customization.

    Defines the contract for formatting output data according to specified styles,
    enabling consistent presentation across different output formats, templates,
    and rendering contexts. Supports extensible formatting strategies for diverse
    output requirements in code generation and reporting workflows.

    Example:
        ```python
        from omnibase_spi.protocols.advanced import ProtocolOutputFormatter
        from omnibase_spi.protocols.types import ProtocolOutputData, ProtocolOutputFormat

        async def format_output(
            formatter: ProtocolOutputFormatter,
            data: ProtocolOutputData,
            style: ProtocolOutputFormat
        ) -> str:
            # Format data with specified style
            formatted = formatter.format(data, style)

            # Output can be written to file or returned
            print(f"Formatted output ({style.format_type}):")
            print(formatted)

            return formatted
        ```

    Key Features:
        - Style-driven output formatting
        - Support for multiple output formats (JSON, YAML, Markdown, etc.)
        - Template-based rendering capabilities
        - Extensible for custom formatting strategies
        - Integration with ONEX code generation pipelines

    See Also:
        - ProtocolOutputFieldTool: Field-level output generation
        - ProtocolStamperEngine: Metadata stamping and enrichment
        - ProtocolLogFormatHandler: Log-specific formatting handlers
    """

    def format(
        self,
        data: ProtocolOutputData,
        style: ProtocolOutputFormat,
    ) -> str:
        """
        Format data according to the specified output style.

        Transforms the input data into a formatted string representation
        based on the provided style configuration. Supports various output
        formats including JSON, YAML, Markdown, and custom templates.

        Args:
            data: The output data to format, containing the content
                and metadata to be rendered.
            style: The output format specification defining the target
                format type, template, and rendering options.

        Returns:
            The formatted string representation of the data according
            to the specified style.

        Raises:
            ValueError: If the data cannot be formatted with the given style.
            TypeError: If the data or style types are incompatible.
        """
        ...
