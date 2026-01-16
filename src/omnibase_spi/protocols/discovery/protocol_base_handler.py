"""
Protocol definition for base handlers.

This protocol provides a minimal protocol interface for handler objects,
enabling type-safe handler patterns without relying on untyped signatures.

Note:
    This is a simplified base handler protocol with a generic ``handle()`` method.
    For the canonical v0.3.0 DI-based protocol handlers (HTTP, Kafka, DB, etc.),
    use :class:`omnibase_spi.protocols.handlers.ProtocolHandler` which provides:
    - handler_type property
    - initialize/shutdown lifecycle methods
    - execute() for protocol-specific operations
    - describe() and health_check() for introspection

See Also:
    :class:`omnibase_spi.protocols.handlers.ProtocolHandler`: Canonical v0.3.0 handler
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolBaseHandler(Protocol):
    """
    Base protocol for simple handlers in the ONEX system.

    Defines a minimal interface for handlers that need only a simple ``handle()``
    method. For more complex handlers requiring lifecycle management, DI support,
    and protocol-specific operations, use ProtocolHandler from protocols.handlers.

    The protocol provides a flexible signature allowing handlers to accept arbitrary
    arguments while maintaining type safety and consistent return semantics.

    Example:
        ```python
        # Implementing a simple handler
        class FileProcessHandler:
            async def handle(self, file_path: str, options: dict[str, object]) -> bool:
                # Process file
                return self._process_file(file_path, options)

        # Using the handler protocol
        handler: ProtocolBaseHandler = FileProcessHandler()
        success = await handler.handle("/path/to/file.txt", {"mode": "read"})

        # Protocol-based handler validation
        def validate_handler(obj: object) -> ProtocolBaseHandler:
            if not isinstance(obj, ProtocolBaseHandler):
                raise TypeError("Object does not implement ProtocolBaseHandler")
            return obj

        # Handler chaining
        async def chain_handlers(
            handlers: list[ProtocolBaseHandler], *args: object
        ) -> bool:
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
        - :class:`omnibase_spi.protocols.handlers.ProtocolHandler`: Canonical DI-based handler
        - ProtocolHandlerDiscovery: Handler discovery and registration
        - ProtocolFileTypeHandler: Specialized file type handling
        - ProtocolEventHandler: Event-specific handling patterns
    """

    async def handle(self, *args: object, **kwargs: object) -> bool: ...
