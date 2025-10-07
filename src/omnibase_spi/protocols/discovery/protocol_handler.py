"""
Protocol definition for generic handlers.

This protocol replaces Any type usage when referring to handler objects
by providing a proper protocol interface.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolHandler(Protocol):
    """
    Base protocol for all handlers in the ONEX system.

    Defines the minimal interface that all handlers must implement across the
    ONEX ecosystem. This protocol establishes a consistent handling pattern for
    various handler types including file handlers, event handlers, request handlers,
    and workflow handlers.

    The protocol provides a flexible signature allowing handlers to accept arbitrary
    arguments while maintaining type safety and consistent return semantics.

    Example:
        ```python
        # Implementing a custom handler
        class FileProcessHandler:
            async def handle(self, file_path: str, options: dict[str, Any]) -> bool:
                # Process file
                return self._process_file(file_path, options)

        # Using the handler protocol
        handler: "ProtocolHandler" = FileProcessHandler()
        success = await handler.handle("/path/to/file.txt", {"mode": "read"})

        # Protocol-based handler validation
        def validate_handler(obj: object) -> "ProtocolHandler":
            if not isinstance(obj, ProtocolHandler):
                raise TypeError("Object does not implement ProtocolHandler")
            return obj

        # Handler chaining
        async def chain_handlers(handlers: list["ProtocolHandler"], *args: Any) -> bool:
            for handler in handlers:
                if not await handler.handle(*args):
                    return False
            return True
        ```

    Key Features:
        - Flexible argument signature for diverse handler types
        - Boolean return for success/failure indication
        - Async-first design for non-blocking operations
        - Runtime type checking with @runtime_checkable
        - Compatible with handler chaining patterns
        - Enables handler composition and strategy patterns

    Handler Categories:
        - File Type Handlers: Process specific file formats
        - Event Handlers: Handle system events and messages
        - Request Handlers: Process HTTP or RPC requests
        - Workflow Handlers: Orchestrate workflow steps
        - Validation Handlers: Perform data validation
        - Transformation Handlers: Transform data between formats

    Return Semantics:
        - True: Handler successfully completed processing
        - False: Handler failed or declined to process
        - May raise exceptions for critical errors

    See Also:
        - ProtocolHandlerDiscovery: Handler discovery and registration
        - ProtocolFileTypeHandler: Specialized file type handling
        - ProtocolEventHandler: Event-specific handling patterns
    """

    async def handle(self, *args: Any, **kwargs: Any) -> bool: ...
