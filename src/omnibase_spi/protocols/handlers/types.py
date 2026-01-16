"""Handler source types and descriptor protocols for ONEX SPI interfaces.

Domain: Handler source classification and handler descriptor protocols.

This module defines the foundational types for classifying handlers based on
their source/origin and provides a protocol for describing handler metadata.

Handler Source Types:
    - BOOTSTRAP: Handlers registered during system initialization (e.g., core handlers)
    - CONTRACT: Handlers discovered and registered via ONEX contracts/manifests
    - HYBRID: Handlers that combine bootstrap registration with contract-driven config

See Also:
    - protocol_handler.py: The main ProtocolHandler interface for I/O handlers
    - docs/architecture/HANDLER_PROTOCOL_DRIVEN_ARCHITECTURE.md
    - omnibase_core: Contains concrete handler implementations and models

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType
    from omnibase_spi.protocols.handlers.protocol_handler import ProtocolHandler

# ==============================================================================
# Handler Source Type Literal
# ==============================================================================

LiteralHandlerSourceType = Literal["BOOTSTRAP", "CONTRACT", "HYBRID"]
"""
Literal type representing the source/origin of a handler registration.

Values:
    BOOTSTRAP: Handler registered during system bootstrap/initialization.
        These are core handlers that are always available and do not depend
        on external contract discovery.

    CONTRACT: Handler discovered and registered via ONEX contract/manifest files.
        These handlers are dynamically loaded based on contract definitions
        and may not be available until contracts are processed.

    HYBRID: Handler that uses bootstrap registration with contract-driven
        configuration. Combines the reliability of bootstrap with the
        flexibility of contract-based configuration.

Example:
    ```python
    def classify_handler(source: LiteralHandlerSourceType) -> str:
        if source == "BOOTSTRAP":
            return "Core handler, always available"
        elif source == "CONTRACT":
            return "Contract-discovered handler"
        else:
            return "Hybrid handler with contract config"
    ```
"""

# ==============================================================================
# Handler Descriptor Protocol
# ==============================================================================


@runtime_checkable
class ProtocolHandlerDescriptor(Protocol):
    """Protocol for handler descriptors providing metadata about registered handlers.

    A handler descriptor provides identification and metadata information about
    a handler for registration and discovery. This enables introspection,
    registry management, and handler discovery.

    Handler descriptors provide a uniform way to describe handlers regardless
    of their source (bootstrap, contract, or hybrid). The runtime uses descriptors
    to register handlers without needing to know how they were discovered.

    This protocol is useful for:
        - Handler registry implementations
        - Handler discovery and selection
        - Debugging and monitoring handler availability
        - Configuration management

    Attributes:
        handler_type: The type identifier for this handler (e.g., "http", "kafka").
            Should match the handler_type property of the corresponding
            ProtocolHandler implementation.
        name: Human-readable name or unique identifier for this handler instance.
            Used for logging, debugging, and handler lookup.
        version: Semantic version string for this handler implementation.
            Follows the "major.minor.patch" format (e.g., "1.0.0").
        metadata: Additional key-value metadata about the handler.
            Can include capabilities, configuration hints, or custom attributes.
        handler: The actual handler instance implementing ProtocolHandler.
        priority: Priority for handler selection when multiple handlers
            of the same type are available. Higher values indicate higher priority.

    Example:
        ```python
        class HttpHandlerDescriptor:
            '''Descriptor for the HTTP REST handler.'''

            @property
            def handler_type(self) -> str:
                return "http"

            @property
            def name(self) -> str:
                return "http-rest-handler"

            @property
            def version(self) -> str:
                return "1.2.0"

            @property
            def metadata(self) -> dict[str, object]:
                return {
                    "capabilities": ["GET", "POST", "PUT", "DELETE"],
                    "supports_streaming": True,
                    "max_connections": 100,
                }

            @property
            def handler(self) -> ProtocolHandler:
                return self._handler

            @property
            def priority(self) -> int:
                return 10

        descriptor = HttpHandlerDescriptor()
        assert isinstance(descriptor, ProtocolHandlerDescriptor)
        print(f"Handler: {descriptor.name} v{descriptor.version}")
        ```

    Note:
        Descriptors are created by handler sources and consumed by the handler
        registry. The runtime should not branch on the source that created the
        descriptor - all descriptors are treated uniformly during registration.

    See Also:
        ProtocolHandler: The main handler interface that performs I/O operations.
        LiteralHandlerSourceType: Classification of how handlers are registered.

    """

    @property
    def handler_type(self) -> str:
        """The type identifier for this handler.

        Returns a string that categorizes the handler by its protocol or
        communication mechanism. Common values include: "http", "kafka",
        "postgresql", "neo4j", "redis", "grpc", "websocket", "file".

        Important:
            This value SHOULD match the ``handler_type`` property of the
            corresponding ``ProtocolHandler`` implementation to ensure
            consistent handler identification across the registry and
            enable proper handler lookup by type.

        Returns:
            String identifier for the handler type.

        """
        ...

    @property
    def name(self) -> str:
        """Human-readable name or unique identifier for this handler.

        The name should be descriptive enough for logging and debugging,
        and unique enough to distinguish between multiple handlers of
        the same type if needed.

        Returns:
            Handler name or identifier string.

        """
        ...

    @property
    def version(self) -> str:
        """Semantic version string for this handler implementation.

        Follows semantic versioning format: "major.minor.patch".
        Used for compatibility checking and upgrade management.

        Returns:
            Version string (e.g., "1.0.0", "2.3.1").

        """
        ...

    @property
    def metadata(self) -> JsonType:
        """Additional key-value metadata about the handler.

        Provides extensible metadata that may include:
            - capabilities: List of supported operations
            - configuration: Default or current configuration values
            - dependencies: Required services or handlers
            - tags: Categorization tags for filtering

        Security:
            NEVER include credentials, API keys, passwords, or other
            sensitive data in metadata. Metadata may be logged, serialized,
            or exposed through administrative/debugging interfaces.

        Returns:
            Dictionary containing handler metadata. May be empty but
            should never be None. Implementations MAY return a reference
            to internal state or a defensive copy - callers SHOULD treat
            the returned dictionary as read-only. Mutating the dictionary
            may have undefined behavior.

        """
        ...

    @property
    def handler(self) -> ProtocolHandler:
        """The actual handler instance implementing ProtocolHandler.

        Provides access to the handler for registration and execution.

        Returns:
            The handler instance.

        """
        ...

    @property
    def priority(self) -> int:
        """Priority for handler selection (higher = preferred).

        When multiple handlers of the same type are registered, the
        handler with the highest priority value is selected by default.

        Recommended Ranges:
            - 0-10: Low priority (fallback handlers)
            - 10-50: Normal priority (default implementations)
            - 50-100: High priority (optimized/specialized handlers)

        Important:
            Priority values are **recommendations, not enforced constraints**.
            The registry does not validate priority values - any integer is
            accepted, including negative values (which would rank lower than
            zero-priority handlers).

            When multiple handlers have **equal priority**, the selection
            order is undefined and may be implementation-specific. Callers
            should not rely on a particular order when priorities are equal.
            To ensure deterministic selection, assign distinct priority values.

        Note:
            A default value of 10 is recommended for standard handlers.
            Priority values are relative within the same handler type;
            comparing priorities across different handler types is not
            meaningful.

        Returns:
            Integer priority value. Higher values indicate higher priority.

        """
        ...


# ==============================================================================
# Module Exports
# ==============================================================================

__all__ = [
    "LiteralHandlerSourceType",
    "ProtocolHandlerDescriptor",
]
