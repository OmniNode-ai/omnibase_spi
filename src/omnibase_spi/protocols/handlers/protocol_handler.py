"""Protocol handler interface for DI-based effect nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.handlers import ModelHandlerDescriptor
    from omnibase_core.models.protocol import (
        ModelConnectionConfig,
        ModelOperationConfig,
        ModelProtocolRequest,
        ModelProtocolResponse,
    )
    from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolHandler(Protocol):
    """Protocol for protocol-specific handlers (HTTP, Kafka, DB, etc.).

    Implementations live in `omnibase_core` or `omnibase_infra`.
    This interface enables dependency injection of I/O handlers
    into effect nodes without tight coupling.

    Handler vs Event Bus Distinction:
        ProtocolHandler is for request-response I/O operations (HTTP, DB, etc.)
        where a direct response is expected. This differs from event bus patterns
        (ProtocolEventPublisher/ProtocolEventConsumer) which handle asynchronous,
        fire-and-forget message passing. Handlers are typically used within effect
        nodes to perform external calls, while event bus protocols coordinate
        inter-service communication.

    Example implementations:
        - HttpRestHandler: HTTP/REST API calls
        - BoltHandler: Neo4j Cypher queries
        - PostgresHandler: SQL queries via asyncpg
        - KafkaHandler: Message publishing

    Migration:
        ProtocolHandlerV3 was the versioned name during the protocol evolution.
        As of v0.3.0, ProtocolHandler is the canonical name. ProtocolHandlerV3
        is provided as a backwards-compatible alias but will be removed in v0.5.0.

        To migrate::

            # Old (deprecated)
            from omnibase_spi.protocols import ProtocolHandlerV3

            # New (recommended)
            from omnibase_spi.protocols import ProtocolHandler

        The protocols are identical - no code changes are needed beyond updating
        the import statement.
    """

    @property
    def handler_type(self) -> str:
        """The type of handler as a string identifier.

        Used for handler identification, routing, and metrics collection.
        Implementations should return a consistent, lowercase string identifier
        that matches the corresponding EnumHandlerType values in omnibase_core.

        Note:
            The return type is ``str`` (not ``EnumHandlerType``) by design to
            maintain SPI/Core decoupling. Implementations may use
            ``EnumHandlerType.value`` or return the string directly.

        Common values: "http", "kafka", "postgresql", "neo4j", "redis",
        "grpc", "websocket", "file", "memory", etc.

        Returns:
            String identifier for the handler type (e.g., ``"http"``, ``"kafka"``).

        """
        ...

    async def initialize(
        self,
        config: ModelConnectionConfig,
    ) -> None:
        """Initialize any clients or connection pools.

        Args:
            config: Connection configuration including URL, auth, pool settings.

        Raises:
            HandlerInitializationError: If initialization fails.

        """
        ...

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """Release resources and close connections.

        Should flush pending operations and release all resources gracefully.

        Args:
            timeout_seconds: Maximum time to wait for shutdown to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If shutdown does not complete within the specified timeout.

        """
        ...

    async def execute(
        self,
        request: ModelProtocolRequest,
        operation_config: ModelOperationConfig,
    ) -> ModelProtocolResponse:
        """Execute a protocol-specific operation.

        Args:
            request: Protocol-agnostic request model from core.
            operation_config: Operation-specific config from core.

        Returns:
            Protocol-agnostic response model from core.

        Raises:
            ProtocolHandlerError: If execution fails.

        """
        ...

    def describe(self) -> ModelHandlerDescriptor:
        """Return handler metadata and capabilities.

        Provides introspection information about the handler including
        its type, supported operations, connection status, and any
        handler-specific capabilities.

        Returns:
            ModelHandlerDescriptor containing handler metadata with fields:
                - handler_type: The handler type (string representation)
                - capabilities: List of supported operations/features
                - version: Handler implementation version (optional)
                - connection_info: Non-sensitive connection details (optional)

            See ``omnibase_core.models.handlers.ModelHandlerDescriptor`` for
            the complete field specification.

        Example:
            ```python
            descriptor = handler.describe()
            print(f"Handler: {descriptor.handler_type}")
            print(f"Capabilities: {descriptor.capabilities}")
            ```

        Security:
            NEVER include in output:
                - Credentials (passwords, API keys, tokens, secrets)
                - Full connection strings with authentication details
                - Internal file paths or system configuration details
                - PII or sensitive business data

            Implementations MUST ensure that ``connection_info`` and any
            optional fields do not expose sensitive data.

        Raises:
            HandlerNotInitializedError: If called before initialize().

        """
        ...

    async def health_check(self) -> JsonType:
        """Check handler health and connectivity.

        Performs a lightweight check to verify the handler is operational
        and can communicate with its backing service.

        Returns:
            Dictionary containing health status:
                - healthy: Boolean indicating overall health
                - latency_ms: Response time in milliseconds (optional)
                - details: Additional diagnostic information (optional)
                - last_error: Most recent error message if unhealthy (optional)

        Example:
            ```python
            health = await handler.health_check()
            if health['healthy']:
                print(f"Handler OK, latency: {health.get('latency_ms', 'N/A')}ms")
            else:
                print(f"Handler unhealthy: {health.get('last_error', 'Unknown')}")
            ```

        Caching:
            Implementations SHOULD cache health check results for 5-30 seconds
            to avoid overwhelming the backend service with repeated health probes.
            Consider using a TTL cache for production deployments.

        Security:
            The ``last_error`` field may contain sensitive information from
            exception messages. Implementations SHOULD sanitize error messages
            before including them by:

                - Removing credentials from connection error text
                - Redacting internal file paths and system details
                - Using generic error categories when possible
                  (e.g., "Connection failed" instead of full stack trace)

            Example of sanitized error::

                {"healthy": False, "last_error": "Connection timeout to database"}

            Instead of::

                {"healthy": False, "last_error": "Connection to postgresql://user:pass@host failed"}

        Raises:
            HandlerNotInitializedError: If called before initialize().

        """
        ...
