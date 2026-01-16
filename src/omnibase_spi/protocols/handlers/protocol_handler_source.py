"""Protocol for handler sources - canonical SPI boundary.

Handler sources provide a uniform interface for discovering handler descriptors
from various backends (bootstrap config, contracts, database, etc.).

This is the canonical SPI protocol - implementations live in omnibase_infra.

The runtime MUST NOT branch on the concrete source type. All handler sources
produce the same output (handler descriptors), enabling uniform handler
registration regardless of source.

See Also:
    - omnibase_core.models.handlers.ModelHandlerDescriptor: The descriptor model
    - docs/architecture/HANDLER_PROTOCOL_DRIVEN_ARCHITECTURE.md

Example:
    ```python
    class BootstrapHandlerSource:
        @property
        def source_type(self) -> str:
            return "BOOTSTRAP"

        def list_handler_descriptors(self) -> tuple[ModelHandlerDescriptor, ...]:
            return (HttpHandlerDescriptor(...), KafkaHandlerDescriptor(...))

        def get_handler_descriptor(self, handler_id: str) -> ModelHandlerDescriptor | None:
            # Lookup by ID
            return self._descriptors.get(handler_id)

    class ContractHandlerSource:
        @property
        def source_type(self) -> str:
            return "CONTRACT"

        def list_handler_descriptors(self) -> tuple[ModelHandlerDescriptor, ...]:
            # Load handlers from contract manifests
            return tuple(self._load_from_manifests())

        def get_handler_descriptor(self, handler_id: str) -> ModelHandlerDescriptor | None:
            for desc in self._descriptors:
                if desc.handler_id == handler_id:
                    return desc
            return None

    # Runtime uses sources uniformly - no branching on source_type
    for source in [bootstrap_source, contract_source]:
        for descriptor in source.list_handler_descriptors():
            registry.register(descriptor)
    ```

.. versionadded:: 0.3.0
    Initial implementation.

.. versionchanged:: 0.4.2
    Changed from async discover_handlers() returning list[ProtocolHandlerDescriptor]
    to sync list_handler_descriptors() returning tuple[ModelHandlerDescriptor, ...].
    Added get_handler_descriptor() for lookup by ID.
    Now uses ModelHandlerDescriptor from omnibase_core (canonical model)
    instead of ProtocolHandlerDescriptor (SPI protocol).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.handlers import ModelHandlerDescriptor


@runtime_checkable
class ProtocolHandlerSource(Protocol):
    """Protocol for handler discovery sources.

    Handler sources provide access to handler descriptors from various
    backends (bootstrap config, contracts, database, etc.).

    This is the canonical SPI protocol - implementations live in omnibase_infra.

    Source Types:
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
        only. All handler sources produce the same output format (a tuple of
        ``ModelHandlerDescriptor`` instances), and the runtime should
        process them identically regardless of their origin.

    Example:
        ```python
        class MyHandlerSource:
            @property
            def source_type(self) -> str:
                return "BOOTSTRAP"

            def list_handler_descriptors(self) -> tuple[ModelHandlerDescriptor, ...]:
                return (
                    HttpHandlerDescriptor(handler_id="http.handler", ...),
                    PostgresHandlerDescriptor(handler_id="pg.handler", ...),
                )

            def get_handler_descriptor(
                self, handler_id: str
            ) -> ModelHandlerDescriptor | None:
                for desc in self.list_handler_descriptors():
                    if desc.handler_id == handler_id:
                        return desc
                return None

        source = MyHandlerSource()
        assert isinstance(source, ProtocolHandlerSource)

        # Runtime registers handlers uniformly
        for descriptor in source.list_handler_descriptors():
            handler_registry.register(descriptor)

        # Lookup specific handler
        http_handler = source.get_handler_descriptor("http.handler")
        ```

    See Also:
        - ``ModelHandlerDescriptor``: The canonical descriptor model from omnibase_core
        - ``ProtocolHandlerRegistry``: Registry that consumes handler descriptors

    """

    @property
    def source_type(self) -> str:
        """The source type identifier (e.g., 'BOOTSTRAP', 'CONTRACT').

        Returns the source classification for observability and debugging.
        The runtime MUST NOT branch on this value - all sources are processed
        identically.

        Common values:
            - ``"BOOTSTRAP"``: Hardcoded handlers registered at startup
            - ``"CONTRACT"``: Dynamically discovered from contracts/manifests
            - ``"HYBRID"``: Combination of bootstrap and contract-based

        Returns:
            String identifier for the handler source type.

        Note:
            This property is intended for logging, metrics, and administrative
            tooling. It should not influence runtime behavior or handler
            selection logic.

        """
        ...

    def list_handler_descriptors(self) -> tuple[ModelHandlerDescriptor, ...]:
        """List all handler descriptors from this source.

        Implementations should return a tuple of handler descriptors for all
        handlers available from this source. The descriptors contain the
        handler metadata needed for registration.

        Returns:
            Tuple of handler descriptors (immutable). May be empty if no
            handlers are available from this source.

        Raises:
            HandlerDiscoveryError: If discovery fails due to configuration
                errors, missing dependencies, or other issues.

        Example:
            ```python
            source = ContractHandlerSource(manifest_path="/etc/handlers/")
            descriptors = source.list_handler_descriptors()

            for desc in descriptors:
                print(f"Found handler: {desc.handler_name} ({desc.handler_type})")
            ```

        Note:
            Returns a tuple (immutable) to ensure thread-safety and prevent
            accidental modification of the descriptor collection.

        """
        ...

    def get_handler_descriptor(self, handler_id: str) -> ModelHandlerDescriptor | None:
        """Get a specific handler descriptor by ID.

        Retrieves a single handler descriptor by its unique identifier.
        This is useful for targeted handler lookup without iterating
        through all descriptors.

        Args:
            handler_id: The unique handler identifier. The format depends
                on the source implementation (e.g., "namespace:name" for
                ModelIdentifier-based lookups, or simple string IDs).

        Returns:
            The handler descriptor if found, None otherwise.

        Example:
            ```python
            source = BootstrapHandlerSource()

            # Lookup specific handler
            descriptor = source.get_handler_descriptor("onex:http-handler")
            if descriptor is not None:
                print(f"Found: {descriptor.handler_name}")
            else:
                print("Handler not found")
            ```

        Note:
            Implementations may use different matching strategies:
            - Exact match on handler_name string representation
            - Match on handler_id field if present
            - Fuzzy matching with namespace resolution

            Callers should consult the specific source implementation
            for the expected ID format.

        """
        ...


__all__ = ["ProtocolHandlerSource"]
