"""Protocol for pluggable log format handlers in ONEX nodes.

This protocol defines the interface that all log format handlers must implement
for consistent, extensible formatting capabilities for different output formats
(JSON, YAML, Markdown, Text, CSV, etc.).

Following the established ONEX architecture patterns for pluggable handlers.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType

# Import LoggerInputState from the canonical location for type hinting.
# Nodes should import their own input state model as needed.


@runtime_checkable
class ProtocolLogFormatHandler(Protocol):
    """
    Protocol for log format handlers in ONEX nodes.

    Each handler is responsible for formatting log entries in a specific output
    format (JSON, YAML, Markdown, Text, CSV, etc.). Handlers must be stateless
    and thread-safe.

    All handlers must declare metadata properties for introspection and plugin
    management, following the established ONEX handler architecture.
    """

    # Required metadata properties for handler introspection
    @property
    def handler_name(self) -> str: ...

    @property
    def handler_version(self) -> str:
        """Version of this handler implementation (e.g., '1.0.0')."""
        ...

    @property
    def handler_author(self) -> str:
        """Author or team responsible for this handler (e.g., 'OmniNode Team')."""
        ...

    @property
    def handler_description(self) -> str:
        """Brief description of what this handler does."""
        ...

    @property
    def supported_formats(self) -> list[str]:
        """List of output formats this handler supports (e.g., ['json'], ['yaml', 'yml'])."""
        ...

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler (higher wins conflicts). Core=100, Runtime=50, Node-local=10, Plugin=0."""
        ...

    @property
    def requires_dependencies(self) -> list[str]:
        """List of optional dependencies required by this handler (e.g., ['yaml', 'csv'])."""
        ...

    # Core handler methods
    async def can_handle(self, format_name: str) -> bool:
        """Return True if this handler can process the given format."""
        ...

    def format_log_entry(self, input_state: object, log_entry: "JsonType") -> str:
        """
        Format a log entry according to this handler's output format.

        Args:
            input_state: Logger input state containing configuration and context
            log_entry: Base log entry structure with timestamp, level, message, etc.

        Returns:
            Formatted log entry as a string

        Raises:
            ModelOnexError: If formatting fails or dependencies are missing
        """
        ...

    def validate_dependencies(self) -> bool:
        """
        Validate that all required dependencies are available.

        Returns:
            True if all dependencies are available, False otherwise
        """
        ...

    async def get_format_metadata(self) -> "JsonType":
        """
        Get metadata about this format handler.

        Returns:
            Dictionary containing format-specific metadata like file extensions,
            MIME types, typical use cases, etc.
        """
        ...
