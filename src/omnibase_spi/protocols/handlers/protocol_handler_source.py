"""
Protocol for handler sources in the ONEX SPI handler framework.

Handler sources provide a uniform interface for discovering handlers,
abstracting away the mechanism by which handlers are obtained (hardcoded
at startup, loaded from contracts, or a combination of both).

The runtime MUST NOT branch on the concrete source type. All handler sources
produce the same output (a list of handler descriptors), enabling uniform
handler registration regardless of source.

See Also:
    docs/architecture/HANDLER_PROTOCOL_DRIVEN_ARCHITECTURE.md

Example:
    ```python
    class BootstrapHandlerSource:
        @property
        def source_type(self) -> LiteralHandlerSourceType:
            return "BOOTSTRAP"

        def discover_handlers(self) -> list[ProtocolHandlerDescriptor]:
            return [HttpHandlerDescriptor(...), KafkaHandlerDescriptor(...)]

    class ContractHandlerSource:
        @property
        def source_type(self) -> LiteralHandlerSourceType:
            return "CONTRACT"

        def discover_handlers(self) -> list[ProtocolHandlerDescriptor]:
            # Load handlers from contract manifests
            return self._load_from_manifests()

    # Runtime uses sources uniformly - no branching on source_type
    for source in [bootstrap_source, contract_source]:
        for descriptor in source.discover_handlers():
            registry.register(descriptor)
    ```
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.handlers.types import (
    LiteralHandlerSourceType,
    ProtocolHandlerDescriptor,
)


@runtime_checkable
class ProtocolHandlerSource(Protocol):
    """
    Protocol for handler sources that provide handler discovery.

    Handler sources abstract the mechanism for obtaining handlers, allowing
    the runtime to work with different discovery strategies uniformly:

    - **BOOTSTRAP**: Handlers that are hardcoded or registered at application
      startup. These are typically core handlers that are always available.

    - **CONTRACT**: Handlers discovered dynamically from contract manifests,
      configuration files, or external registries. These may be loaded
      lazily or refreshed at runtime.

    - **HYBRID**: A combination of bootstrap and contract-based discovery,
      where some handlers are always available and others are discovered
      dynamically.

    Important:
        The runtime MUST NOT branch on ``source_type``. The source type is
        provided for observability, debugging, and administrative purposes
        only. All handler sources produce the same output format (a list of
        ``ProtocolHandlerDescriptor`` instances), and the runtime should
        process them identically regardless of their origin.

    Example:
        ```python
        class MyHandlerSource:
            @property
            def source_type(self) -> LiteralHandlerSourceType:
                return "BOOTSTRAP"

            def discover_handlers(self) -> list[ProtocolHandlerDescriptor]:
                return [
                    HttpHandlerDescriptor(handler=http_handler),
                    PostgresHandlerDescriptor(handler=pg_handler),
                ]

        source = MyHandlerSource()
        assert isinstance(source, ProtocolHandlerSource)

        # Runtime registers handlers uniformly
        for descriptor in source.discover_handlers():
            handler_registry.register(descriptor)
        ```

    See Also:
        - ``ProtocolHandlerDescriptor``: The descriptor type returned by sources
        - ``ProtocolHandlerRegistry``: Registry that consumes handler descriptors
        - ``LiteralHandlerSourceType``: The allowed source type values
    """

    @property
    def source_type(self) -> LiteralHandlerSourceType:
        """
        The type of handler source.

        Returns the source classification for observability and debugging.
        The runtime MUST NOT branch on this value - all sources are processed
        identically.

        Returns:
            One of:
            - ``"BOOTSTRAP"``: Hardcoded handlers registered at startup
            - ``"CONTRACT"``: Dynamically discovered from contracts/manifests
            - ``"HYBRID"``: Combination of bootstrap and contract-based

        Note:
            This property is intended for logging, metrics, and administrative
            tooling. It should not influence runtime behavior or handler
            selection logic.
        """
        ...

    def discover_handlers(self) -> list[ProtocolHandlerDescriptor]:
        """
        Discover and return all handlers from this source.

        Implementations should return a list of handler descriptors for all
        handlers available from this source. The descriptors contain the
        handler instances along with metadata needed for registration.

        Returns:
            List of handler descriptors. May be empty if no handlers are
            available from this source.

        Raises:
            HandlerDiscoveryError: If discovery fails due to configuration
                errors, missing dependencies, or other issues.

        Example:
            ```python
            source = ContractHandlerSource(manifest_path="/etc/handlers/")
            descriptors = source.discover_handlers()

            for desc in descriptors:
                print(f"Found handler: {desc.handler_id} ({desc.handler_type})")
            ```

        Note:
            This method may be called multiple times during the application
            lifecycle (e.g., for handler refresh). Implementations should
            be idempotent and thread-safe if concurrent discovery is possible.
        """
        ...
